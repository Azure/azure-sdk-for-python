```py
namespace azure.mgmt.azurearcdata

    class azure.mgmt.azurearcdata.AzureArcDataManagementClient: implements ContextManager 
        active_directory_connectors: ActiveDirectoryConnectorsOperations
        data_controllers: DataControllersOperations
        failover_groups: FailoverGroupsOperations
        operations: Operations
        postgres_instances: PostgresInstancesOperations
        sql_managed_instances: SqlManagedInstancesOperations
        sql_server_availability_groups: SqlServerAvailabilityGroupsOperations
        sql_server_databases: SqlServerDatabasesOperations
        sql_server_esu_licenses: SqlServerEsuLicensesOperations
        sql_server_instances: SqlServerInstancesOperations
        sql_server_licenses: SqlServerLicensesOperations

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


namespace azure.mgmt.azurearcdata.aio

    class azure.mgmt.azurearcdata.aio.AzureArcDataManagementClient: implements AsyncContextManager 
        active_directory_connectors: ActiveDirectoryConnectorsOperations
        data_controllers: DataControllersOperations
        failover_groups: FailoverGroupsOperations
        operations: Operations
        postgres_instances: PostgresInstancesOperations
        sql_managed_instances: SqlManagedInstancesOperations
        sql_server_availability_groups: SqlServerAvailabilityGroupsOperations
        sql_server_databases: SqlServerDatabasesOperations
        sql_server_esu_licenses: SqlServerEsuLicensesOperations
        sql_server_instances: SqlServerInstancesOperations
        sql_server_licenses: SqlServerLicensesOperations

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


namespace azure.mgmt.azurearcdata.aio.operations

    class azure.mgmt.azurearcdata.aio.operations.ActiveDirectoryConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: ActiveDirectoryConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ActiveDirectoryConnectorResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: ActiveDirectoryConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ActiveDirectoryConnectorResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ActiveDirectoryConnectorResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                **kwargs: Any
            ) -> ActiveDirectoryConnectorResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ActiveDirectoryConnectorResource]: ...


    class azure.mgmt.azurearcdata.aio.operations.DataControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @overload
        async def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataControllerResource]: ...

        @distributed_trace_async
        async def get_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                **kwargs: Any
            ) -> DataControllerResource: ...

        @distributed_trace
        def list_in_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataControllerResource]: ...

        @distributed_trace
        def list_in_subscription(self, **kwargs: Any) -> AsyncItemPaged[DataControllerResource]: ...


    class azure.mgmt.azurearcdata.aio.operations.FailoverGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                failover_group_resource: FailoverGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverGroupResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                failover_group_resource: FailoverGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverGroupResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                failover_group_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverGroupResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                **kwargs: Any
            ) -> FailoverGroupResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FailoverGroupResource]: ...


    class azure.mgmt.azurearcdata.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.azurearcdata.aio.operations.PostgresInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: PostgresInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostgresInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: PostgresInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostgresInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostgresInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[PostgresInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PostgresInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: PostgresInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: PostgresInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlManagedInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: SqlManagedInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlManagedInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: SqlManagedInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlManagedInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlManagedInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SqlManagedInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlManagedInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: SqlManagedInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: SqlManagedInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlServerAvailabilityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        async def add_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        async def add_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        async def begin_create_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_ag_configuration: AvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_ag_configuration: AvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_ag_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_distributed_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_dag_configuration: DistributedAvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_distributed_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_dag_configuration: DistributedAvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_distributed_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_dag_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_managed_instance_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_managed_instance_link_configuration: ManagedInstanceLinkCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_managed_instance_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_managed_instance_link_configuration: ManagedInstanceLinkCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_create_managed_instance_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_managed_instance_link_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_failover_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                managed_instance_resource_id: FailoverMiLinkResourceId, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_failover_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                managed_instance_resource_id: FailoverMiLinkResourceId, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_failover_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                managed_instance_resource_id: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_update: SqlServerAvailabilityGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_update: SqlServerAvailabilityGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_resource: SqlServerAvailabilityGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_resource: SqlServerAvailabilityGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace_async
        async def detail_view(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace_async
        async def failover(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace_async
        async def force_failover_allow_data_loss(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def remove_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        async def remove_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        async def remove_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlServerDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_update: SqlServerDatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerDatabaseResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_update: SqlServerDatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerDatabaseResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerDatabaseResource]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_resource: SqlServerDatabaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_resource: SqlServerDatabaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerDatabaseResource]: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlServerEsuLicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                sql_server_esu_license: SqlServerEsuLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                sql_server_esu_license: SqlServerEsuLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                sql_server_esu_license: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SqlServerEsuLicense]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerEsuLicense]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                parameters: SqlServerEsuLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                parameters: SqlServerEsuLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlServerInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: SqlServerInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: SqlServerInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_bpa_request: SqlServerInstanceBpaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[List[str]]]: ...

        @overload
        async def begin_get_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_bpa_request: SqlServerInstanceBpaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[List[str]]]: ...

        @overload
        async def begin_get_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_bpa_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[List[str]]]: ...

        @overload
        async def begin_get_jobs(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_request: Optional[SqlServerInstanceJobsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceJobsResponse]: ...

        @overload
        async def begin_get_jobs(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_request: Optional[SqlServerInstanceJobsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceJobsResponse]: ...

        @overload
        async def begin_get_jobs(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceJobsResponse]: ...

        @distributed_trace_async
        async def begin_get_migration_readiness_report(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceMigrationReadinessReportResponse]: ...

        @overload
        async def begin_get_target_recommendation_reports(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_target_recommendation_reports_request: Optional[SqlServerInstanceTargetRecommendationReportsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceTargetRecommendationReportsResponse]: ...

        @overload
        async def begin_get_target_recommendation_reports(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_target_recommendation_reports_request: Optional[SqlServerInstanceTargetRecommendationReportsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceTargetRecommendationReportsResponse]: ...

        @overload
        async def begin_get_target_recommendation_reports(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_target_recommendation_reports_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceTargetRecommendationReportsResponse]: ...

        @overload
        async def begin_get_telemetry(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_telemetry_request: SqlServerInstanceTelemetryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[List[str]]]: ...

        @overload
        async def begin_get_telemetry(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_telemetry_request: SqlServerInstanceTelemetryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[List[str]]]: ...

        @overload
        async def begin_get_telemetry(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_telemetry_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[List[str]]]: ...

        @distributed_trace_async
        async def begin_run_best_practice_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceRunBestPracticesAssessmentResponse]: ...

        @overload
        async def begin_run_managed_instance_link_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_managed_instance_link_assessment_request: SqlServerInstanceManagedInstanceLinkAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceManagedInstanceLinkAssessmentResponse]: ...

        @overload
        async def begin_run_managed_instance_link_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_managed_instance_link_assessment_request: SqlServerInstanceManagedInstanceLinkAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceManagedInstanceLinkAssessmentResponse]: ...

        @overload
        async def begin_run_managed_instance_link_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_managed_instance_link_assessment_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceManagedInstanceLinkAssessmentResponse]: ...

        @distributed_trace_async
        async def begin_run_migration_readiness_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceRunMigrationReadinessAssessmentResponse]: ...

        @overload
        async def begin_run_target_recommendation_job(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_run_target_recommendation_job_request: Optional[SqlServerInstanceRunTargetRecommendationJobRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceRunTargetRecommendationJobResponse]: ...

        @overload
        async def begin_run_target_recommendation_job(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_run_target_recommendation_job_request: Optional[SqlServerInstanceRunTargetRecommendationJobRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceRunTargetRecommendationJobResponse]: ...

        @overload
        async def begin_run_target_recommendation_job(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_run_target_recommendation_job_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstanceRunTargetRecommendationJobResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: SqlServerInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: SqlServerInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlServerInstance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @overload
        def get_all_availability_groups(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_retrieval_filters: Optional[AvailabilityGroupRetrievalFilters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        def get_all_availability_groups(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_retrieval_filters: Optional[AvailabilityGroupRetrievalFilters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        def get_all_availability_groups(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_retrieval_filters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        async def get_jobs_status(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_status_request: Optional[SqlServerInstanceJobsStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstanceJobsStatusResponse: ...

        @overload
        async def get_jobs_status(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_status_request: Optional[SqlServerInstanceJobsStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstanceJobsStatusResponse: ...

        @overload
        async def get_jobs_status(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_status_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstanceJobsStatusResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SqlServerInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerInstance]: ...

        @distributed_trace_async
        async def post_upgrade(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @distributed_trace_async
        async def pre_upgrade(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @distributed_trace_async
        async def run_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstanceRunBestPracticesAssessmentResponse: ...

        @distributed_trace_async
        async def run_migration_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstanceRunMigrationAssessmentResponse: ...


    class azure.mgmt.azurearcdata.aio.operations.SqlServerLicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                sql_server_license: SqlServerLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                sql_server_license: SqlServerLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                sql_server_license: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SqlServerLicense]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlServerLicense]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                parameters: SqlServerLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                parameters: SqlServerLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...


namespace azure.mgmt.azurearcdata.models

    class azure.mgmt.azurearcdata.models.AccountProvisioningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"


    class azure.mgmt.azurearcdata.models.ActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        DEACTIVATED = "Deactivated"


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorDNSDetails(_Model):
        domain_name: Optional[str]
        nameserver_ip_addresses: list[str]
        prefer_k8_s_dns_for_ptr_lookups: Optional[bool]
        replicas: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                nameserver_ip_addresses: list[str], 
                prefer_k8_s_dns_for_ptr_lookups: Optional[bool] = ..., 
                replicas: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorDomainDetails(_Model):
        domain_controllers: Optional[ActiveDirectoryDomainControllers]
        netbios_domain_name: Optional[str]
        ou_distinguished_name: Optional[str]
        realm: str
        service_account_provisioning: Optional[Union[str, AccountProvisioningMode]]

        @overload
        def __init__(
                self, 
                *, 
                domain_controllers: Optional[ActiveDirectoryDomainControllers] = ..., 
                netbios_domain_name: Optional[str] = ..., 
                ou_distinguished_name: Optional[str] = ..., 
                realm: str, 
                service_account_provisioning: Optional[Union[str, AccountProvisioningMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorProperties(_Model):
        domain_service_account_login_information: Optional[BasicLoginInformation]
        provisioning_state: Optional[str]
        spec: ActiveDirectoryConnectorSpec
        status: Optional[ActiveDirectoryConnectorStatus]

        @overload
        def __init__(
                self, 
                *, 
                domain_service_account_login_information: Optional[BasicLoginInformation] = ..., 
                spec: ActiveDirectoryConnectorSpec, 
                status: Optional[ActiveDirectoryConnectorStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorResource(ProxyResource):
        id: str
        name: str
        properties: ActiveDirectoryConnectorProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: ActiveDirectoryConnectorProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorSpec(_Model):
        active_directory: ActiveDirectoryConnectorDomainDetails
        dns: ActiveDirectoryConnectorDNSDetails

        @overload
        def __init__(
                self, 
                *, 
                active_directory: ActiveDirectoryConnectorDomainDetails, 
                dns: ActiveDirectoryConnectorDNSDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryConnectorStatus(_Model):
        last_update_time: Optional[str]
        observed_generation: Optional[int]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_update_time: Optional[str] = ..., 
                observed_generation: Optional[int] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryDomainController(_Model):
        hostname: str

        @overload
        def __init__(
                self, 
                *, 
                hostname: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryDomainControllers(_Model):
        primary_domain_controller: Optional[ActiveDirectoryDomainController]
        secondary_domain_controllers: Optional[list[ActiveDirectoryDomainController]]

        @overload
        def __init__(
                self, 
                *, 
                primary_domain_controller: Optional[ActiveDirectoryDomainController] = ..., 
                secondary_domain_controllers: Optional[list[ActiveDirectoryDomainController]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ActiveDirectoryInformation(_Model):
        keytab_information: Optional[KeytabInformation]

        @overload
        def __init__(
                self, 
                *, 
                keytab_information: Optional[KeytabInformation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AdditionalMigrationJobAttributes(_Model):
        key_name: Optional[str]
        key_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        SUM = "Sum"


    class azure.mgmt.azurearcdata.models.AlwaysOnRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY_GROUP_REPLICA = "AvailabilityGroupReplica"
        FAILOVER_CLUSTER_INSTANCE = "FailoverClusterInstance"
        FAILOVER_CLUSTER_NODE = "FailoverClusterNode"
        NONE = "None"


    class azure.mgmt.azurearcdata.models.ArcSqlManagedInstanceLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE_PRICE = "BasePrice"
        DISASTER_RECOVERY = "DisasterRecovery"
        LICENSE_INCLUDED = "LicenseIncluded"


    class azure.mgmt.azurearcdata.models.ArcSqlServerAvailabilityGroupTypeFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINED = "CONTAINED"
        DEFAULT = "DEFAULT"
        DISTRIBUTED = "DISTRIBUTED"


    class azure.mgmt.azurearcdata.models.ArcSqlServerAvailabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYNCHRONOUS_COMMIT = "ASYNCHRONOUS_COMMIT"
        SYNCHRONOUS_COMMIT = "SYNCHRONOUS_COMMIT"


    class azure.mgmt.azurearcdata.models.ArcSqlServerFailoverMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "AUTOMATIC"
        EXTERNAL = "EXTERNAL"
        MANUAL = "MANUAL"
        NONE = "NONE"


    class azure.mgmt.azurearcdata.models.ArcSqlServerLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FABRIC_CAPACITY = "FabricCapacity"
        FREE = "Free"
        HADR = "HADR"
        LICENSE_ONLY = "LicenseOnly"
        PAID = "Paid"
        PAYG = "PAYG"
        SERVER_CAL = "ServerCAL"
        UNDEFINED = "Undefined"


    class azure.mgmt.azurearcdata.models.AssessmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "Failure"
        SUCCESS = "Success"
        WARNING = "Warning"


    class azure.mgmt.azurearcdata.models.Authentication(_Model):
        mode: Optional[Union[str, Mode]]
        sql_server_entra_identity: Optional[list[EntraAuthentication]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, Mode]] = ..., 
                sql_server_entra_identity: Optional[list[EntraAuthentication]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AutomatedBackupPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "NONE"
        PRIMARY = "PRIMARY"
        SECONDARY = "SECONDARY"
        SECONDARY_ONLY = "SECONDARY_ONLY"


    class azure.mgmt.azurearcdata.models.AvailabilityGroupConfigure(_Model):
        availability_mode: Optional[Union[str, ArcSqlServerAvailabilityMode]]
        availability_mode_description: Optional[str]
        backup_priority: Optional[int]
        certificate_name: Optional[str]
        endpoint_authentication_mode: Optional[Union[str, ConnectionAuth]]
        endpoint_connect_login: Optional[str]
        endpoint_name: Optional[str]
        endpoint_url: Optional[str]
        failover_mode: Optional[Union[str, ArcSqlServerFailoverMode]]
        failover_mode_description: Optional[str]
        primary_allow_connections: Optional[Union[str, PrimaryAllowConnections]]
        primary_role_allow_connections_description: Optional[str]
        read_only_routing_url: Optional[str]
        read_write_routing_url: Optional[str]
        replica_create_date: Optional[datetime]
        replica_modify_date: Optional[datetime]
        secondary_allow_connections: Optional[Union[str, SecondaryAllowConnections]]
        secondary_role_allow_connections_description: Optional[str]
        seeding_mode: Optional[Union[str, SeedingMode]]
        seeding_mode_description: Optional[str]
        session_timeout: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                availability_mode: Optional[Union[str, ArcSqlServerAvailabilityMode]] = ..., 
                backup_priority: Optional[int] = ..., 
                certificate_name: Optional[str] = ..., 
                endpoint_authentication_mode: Optional[Union[str, ConnectionAuth]] = ..., 
                endpoint_connect_login: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                endpoint_url: Optional[str] = ..., 
                failover_mode: Optional[Union[str, ArcSqlServerFailoverMode]] = ..., 
                primary_allow_connections: Optional[Union[str, PrimaryAllowConnections]] = ..., 
                read_only_routing_url: Optional[str] = ..., 
                read_write_routing_url: Optional[str] = ..., 
                secondary_allow_connections: Optional[Union[str, SecondaryAllowConnections]] = ..., 
                seeding_mode: Optional[Union[str, SeedingMode]] = ..., 
                session_timeout: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AvailabilityGroupCreateUpdateConfiguration(_Model):
        automated_backup_preference: Optional[Union[str, AutomatedBackupPreference]]
        availability_group_name: Optional[str]
        cluster_type: Optional[Union[str, ClusterType]]
        databases: Optional[list[str]]
        db_failover: Optional[Union[str, DbFailover]]
        dtc_support: Optional[Union[str, DtcSupport]]
        failure_condition_level: Optional[Union[int, FailureConditionLevel]]
        health_check_timeout: Optional[int]
        listener: Optional[SqlAvailabilityGroupStaticIPListenerProperties]
        replicas: Optional[list[AvailabilityGroupCreateUpdateReplicaConfiguration]]
        required_synchronized_secondaries_to_commit: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                automated_backup_preference: Optional[Union[str, AutomatedBackupPreference]] = ..., 
                availability_group_name: Optional[str] = ..., 
                cluster_type: Optional[Union[str, ClusterType]] = ..., 
                databases: Optional[list[str]] = ..., 
                db_failover: Optional[Union[str, DbFailover]] = ..., 
                dtc_support: Optional[Union[str, DtcSupport]] = ..., 
                failure_condition_level: Optional[Union[int, FailureConditionLevel]] = ..., 
                health_check_timeout: Optional[int] = ..., 
                listener: Optional[SqlAvailabilityGroupStaticIPListenerProperties] = ..., 
                replicas: Optional[list[AvailabilityGroupCreateUpdateReplicaConfiguration]] = ..., 
                required_synchronized_secondaries_to_commit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AvailabilityGroupCreateUpdateReplicaConfiguration(_Model):
        availability_mode: Optional[Union[str, ArcSqlServerAvailabilityMode]]
        backup_priority: Optional[int]
        certificate_name: Optional[str]
        endpoint_authentication_mode: Optional[Union[str, ConnectionAuth]]
        endpoint_connect_login: Optional[str]
        endpoint_name: Optional[str]
        endpoint_url: Optional[str]
        failover_mode: Optional[Union[str, ArcSqlServerFailoverMode]]
        primary_role_allow_connections: Optional[Union[str, PrimaryAllowConnections]]
        primary_role_read_only_routing_list: Optional[list[str]]
        secondary_role_allow_connections: Optional[Union[str, SecondaryAllowConnections]]
        secondary_role_read_only_routing_url: Optional[str]
        seeding_mode: Optional[Union[str, SeedingMode]]
        server_instance: Optional[str]
        session_timeout: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                availability_mode: Optional[Union[str, ArcSqlServerAvailabilityMode]] = ..., 
                backup_priority: Optional[int] = ..., 
                certificate_name: Optional[str] = ..., 
                endpoint_authentication_mode: Optional[Union[str, ConnectionAuth]] = ..., 
                endpoint_connect_login: Optional[str] = ..., 
                endpoint_name: Optional[str] = ..., 
                endpoint_url: Optional[str] = ..., 
                failover_mode: Optional[Union[str, ArcSqlServerFailoverMode]] = ..., 
                primary_role_allow_connections: Optional[Union[str, PrimaryAllowConnections]] = ..., 
                primary_role_read_only_routing_list: Optional[list[str]] = ..., 
                secondary_role_allow_connections: Optional[Union[str, SecondaryAllowConnections]] = ..., 
                secondary_role_read_only_routing_url: Optional[str] = ..., 
                seeding_mode: Optional[Union[str, SeedingMode]] = ..., 
                server_instance: Optional[str] = ..., 
                session_timeout: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AvailabilityGroupInfo(_Model):
        automated_backup_preference_description: Optional[str]
        basic_features: Optional[bool]
        cluster_type_description: Optional[str]
        db_failover: Optional[bool]
        dtc_support: Optional[bool]
        failure_condition_level: Optional[int]
        health_check_timeout: Optional[int]
        is_contained: Optional[bool]
        is_distributed: Optional[bool]
        listener: Optional[SqlAvailabilityGroupStaticIPListenerProperties]
        primary_recovery_health_description: Optional[str]
        primary_replica: Optional[str]
        replication_partner_type: Optional[Union[str, ReplicationPartnerType]]
        required_synchronized_secondaries_to_commit: Optional[int]
        secondary_recovery_health_description: Optional[str]
        synchronization_health_description: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                basic_features: Optional[bool] = ..., 
                db_failover: Optional[bool] = ..., 
                dtc_support: Optional[bool] = ..., 
                failure_condition_level: Optional[int] = ..., 
                health_check_timeout: Optional[int] = ..., 
                is_contained: Optional[bool] = ..., 
                is_distributed: Optional[bool] = ..., 
                listener: Optional[SqlAvailabilityGroupStaticIPListenerProperties] = ..., 
                required_synchronized_secondaries_to_commit: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AvailabilityGroupRetrievalFilters(_Model):
        availability_group_type_filter: Optional[Union[str, ArcSqlServerAvailabilityGroupTypeFilter]]
        replication_partner_type_filter: Optional[Union[str, ReplicationPartnerType]]

        @overload
        def __init__(
                self, 
                *, 
                availability_group_type_filter: Optional[Union[str, ArcSqlServerAvailabilityGroupTypeFilter]] = ..., 
                replication_partner_type_filter: Optional[Union[str, ReplicationPartnerType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.AvailabilityGroupState(_Model):
        availability_group_replica_role: Optional[str]
        connected_state_description: Optional[str]
        last_connect_error_description: Optional[str]
        last_connect_error_timestamp: Optional[datetime]
        operational_state_description: Optional[str]
        recovery_health_description: Optional[str]
        synchronization_health_description: Optional[str]


    class azure.mgmt.azurearcdata.models.AzureManagedInstanceRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.azurearcdata.models.BackgroundJob(_Model):
        end_time: Optional[datetime]
        execution_state: Optional[Union[str, ExecutionState]]
        last_execution_status: Optional[Union[str, LastExecutionStatus]]
        last_execution_time: Optional[datetime]
        next_execution_time: Optional[datetime]
        start_time: Optional[datetime]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                execution_state: Optional[Union[str, ExecutionState]] = ..., 
                last_execution_status: Optional[Union[str, LastExecutionStatus]] = ..., 
                last_execution_time: Optional[datetime] = ..., 
                next_execution_time: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.BackupPolicy(_Model):
        differential_backup_hours: Optional[Union[int, DifferentialBackupHours]]
        full_backup_days: Optional[int]
        retention_period_days: Optional[int]
        transaction_log_backup_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                differential_backup_hours: Optional[Union[int, DifferentialBackupHours]] = ..., 
                full_backup_days: Optional[int] = ..., 
                retention_period_days: Optional[int] = ..., 
                transaction_log_backup_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.BasicLoginInformation(_Model):
        password: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.BestPracticesAssessment(_Model):
        enabled: Optional[bool]
        schedule: Optional[Schedule]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                schedule: Optional[Schedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.BillingPlan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAID = "Paid"
        PAYG = "PAYG"


    class azure.mgmt.azurearcdata.models.ClientConnection(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ClusterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "NONE"
        WSFC = "WSFC"


    class azure.mgmt.azurearcdata.models.CommonSku(_Model):
        capacity: Optional[int]
        dev: Optional[bool]
        family: Optional[str]
        name: str
        size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                dev: Optional[bool] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ConnectionAuth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CERTIFICATE = "Certificate"
        CERTIFICATE_WINDOWS_KERBEROS = "Certificate_Windows_Kerberos"
        CERTIFICATE_WINDOWS_NEGOTIATE = "Certificate_Windows_Negotiate"
        CERTIFICATE_WINDOWS_NTLM = "Certificate_Windows_NTLM"
        WINDOWS_KERBEROS = "Windows_Kerberos"
        WINDOWS_KERBEROS_CERTIFICATE = "Windows_Kerberos_Certificate"
        WINDOWS_NEGOTIATE = "Windows_Negotiate"
        WINDOWS_NEGOTIATE_CERTIFICATE = "Windows_Negotiate_Certificate"
        WINDOWS_NTLM = "Windows_NTLM"
        WINDOWS_NTLM_CERTIFICATE = "Windows_NTLM_Certificate"


    class azure.mgmt.azurearcdata.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        DISCOVERED = "Discovered"
        REGISTERED = "Registered"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.CostOptionSelectedValues(_Model):
        compute_and_storage_cost_option: Optional[str]
        sql_license_cost_option: Optional[str]
        windows_license_cost_option: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compute_and_storage_cost_option: Optional[str] = ..., 
                sql_license_cost_option: Optional[str] = ..., 
                windows_license_cost_option: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.CostTypeValues(_Model):
        compute_cost: Optional[float]
        iops_cost: Optional[float]
        storage_cost: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                compute_cost: Optional[float] = ..., 
                iops_cost: Optional[float] = ..., 
                storage_cost: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.azurearcdata.models.CronTrigger(_Model):
        expression: Optional[str]
        start_time: Optional[str]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expression: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DBMEndpoint(_Model):
        certificate_expiry_date: Optional[datetime]
        certificate_name: Optional[str]
        connection_auth: Optional[Union[str, ConnectionAuth]]
        encryption_algorithm: Optional[Union[str, EncryptionAlgorithm]]
        endpoint_name: Optional[str]
        ip_address: Optional[str]
        is_dynamic_port: Optional[bool]
        is_encryption_enabled: Optional[bool]
        port: Optional[int]
        role: Optional[Union[str, Role]]


    class azure.mgmt.azurearcdata.models.DataBaseMigration(_Model):
        assessment: Optional[DataBaseMigrationAssessment]
        jobs: Optional[list[DatabaseMigrationJobsItem]]

        @overload
        def __init__(
                self, 
                *, 
                assessment: Optional[DataBaseMigrationAssessment] = ..., 
                jobs: Optional[list[DatabaseMigrationJobsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DataBaseMigrationAssessment(_Model):
        assessment_upload_time: Optional[datetime]
        database_assessments: Optional[list[DatabaseAssessmentsItem]]
        target_readiness: Optional[TargetReadiness]
        target_recommendation_generation_time: Optional[datetime]


    class azure.mgmt.azurearcdata.models.DataControllerProperties(_Model):
        basic_login_information: Optional[BasicLoginInformation]
        cluster_id: Optional[str]
        extension_id: Optional[str]
        infrastructure: Optional[Union[str, Infrastructure]]
        k8_s_raw: Optional[Any]
        last_uploaded_date: Optional[datetime]
        log_analytics_workspace_config: Optional[LogAnalyticsWorkspaceConfig]
        logs_dashboard_credential: Optional[BasicLoginInformation]
        metrics_dashboard_credential: Optional[BasicLoginInformation]
        on_premise_property: Optional[OnPremiseProperty]
        provisioning_state: Optional[str]
        upload_service_principal: Optional[UploadServicePrincipal]
        upload_watermark: Optional[UploadWatermark]

        @overload
        def __init__(
                self, 
                *, 
                basic_login_information: Optional[BasicLoginInformation] = ..., 
                cluster_id: Optional[str] = ..., 
                extension_id: Optional[str] = ..., 
                infrastructure: Optional[Union[str, Infrastructure]] = ..., 
                k8_s_raw: Optional[Any] = ..., 
                last_uploaded_date: Optional[datetime] = ..., 
                log_analytics_workspace_config: Optional[LogAnalyticsWorkspaceConfig] = ..., 
                logs_dashboard_credential: Optional[BasicLoginInformation] = ..., 
                metrics_dashboard_credential: Optional[BasicLoginInformation] = ..., 
                on_premise_property: Optional[OnPremiseProperty] = ..., 
                upload_service_principal: Optional[UploadServicePrincipal] = ..., 
                upload_watermark: Optional[UploadWatermark] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DataControllerResource(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: DataControllerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: DataControllerProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DataControllerUpdate(_Model):
        properties: Optional[DataControllerProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DataControllerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DatabaseAssessmentsItem(_Model):
        applies_to_migration_target_platform: Optional[str]
        feature_id: Optional[str]
        issue_category: Optional[str]
        more_information: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                applies_to_migration_target_platform: Optional[str] = ..., 
                feature_id: Optional[str] = ..., 
                issue_category: Optional[str] = ..., 
                more_information: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DatabaseCreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"


    class azure.mgmt.azurearcdata.models.DatabaseMigrationJobsItem(_Model):
        additional_attributes: Optional[list[AdditionalMigrationJobAttributes]]
        end_time: Optional[datetime]
        initiated_from: Optional[Union[str, InitiatedFrom]]
        last_error: Optional[str]
        migration_mode: Optional[Union[str, MigrationMode]]
        migration_tracking_id: Optional[str]
        start_time: Optional[datetime]
        status: Optional[Union[str, MigrationStatus]]
        target_resource_id: Optional[str]
        target_type: Optional[Union[str, TargetType]]

        @overload
        def __init__(
                self, 
                *, 
                additional_attributes: Optional[list[AdditionalMigrationJobAttributes]] = ..., 
                end_time: Optional[datetime] = ..., 
                initiated_from: Optional[Union[str, InitiatedFrom]] = ..., 
                last_error: Optional[str] = ..., 
                migration_mode: Optional[Union[str, MigrationMode]] = ..., 
                migration_tracking_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, MigrationStatus]] = ..., 
                target_resource_id: Optional[str] = ..., 
                target_type: Optional[Union[str, TargetType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DatabaseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPYING = "Copying"
        EMERGENCY = "Emergency"
        OFFLINE = "Offline"
        OFFLINE_SECONDARY = "OfflineSecondary"
        ONLINE = "Online"
        RECOVERING = "Recovering"
        RECOVERY_PENDING = "RecoveryPending"
        RESTORING = "Restoring"
        SUSPECT = "Suspect"


    class azure.mgmt.azurearcdata.models.Databases(_Model):
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DbFailover(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "OFF"
        ON = "ON"


    class azure.mgmt.azurearcdata.models.DefenderStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROTECTED = "Protected"
        UNKNOWN = "Unknown"
        UNPROTECTED = "Unprotected"


    class azure.mgmt.azurearcdata.models.DifferentialBackupHours(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        TWELVE = 12
        TWENTY_FOUR = 24


    class azure.mgmt.azurearcdata.models.DiscoverySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADS = "ADS"
        AZURE_ARC = "Azure Arc"
        AZURE_MIGRATE = "Azure Migrate"
        DMS_CLI = "DMS-CLI"
        DMS_PORTAL = "DMS-Portal"
        DMS_PS = "DMS-PS"
        DMS_SDK = "DMS-SDK"
        IMPORT = "Import"
        OTHER = "Other"
        SSMA = "SSMA"
        SSMS = "SSMS"


    class azure.mgmt.azurearcdata.models.DiskSizes(_Model):
        caching: Optional[str]
        disk_type: Optional[str]
        max_iops: Optional[float]
        max_size_in_gib: Optional[float]
        max_throughput_in_mbps: Optional[float]
        redundancy: Optional[str]
        size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[str] = ..., 
                disk_type: Optional[str] = ..., 
                max_iops: Optional[float] = ..., 
                max_size_in_gib: Optional[float] = ..., 
                max_throughput_in_mbps: Optional[float] = ..., 
                redundancy: Optional[str] = ..., 
                size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DistributedAvailabilityGroupCreateUpdateAvailabilityGroupCertificateConfiguration(_Model):
        certificate_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration(_Model):
        availability_group: Optional[str]
        availability_mode: Optional[Union[str, ArcSqlServerAvailabilityMode]]
        certificate_configuration: Optional[DistributedAvailabilityGroupCreateUpdateAvailabilityGroupCertificateConfiguration]
        failover_mode: Optional[Union[str, ArcSqlServerFailoverMode]]
        listener_url: Optional[str]
        seeding_mode: Optional[Union[str, SeedingMode]]

        @overload
        def __init__(
                self, 
                *, 
                availability_group: Optional[str] = ..., 
                availability_mode: Optional[Union[str, ArcSqlServerAvailabilityMode]] = ..., 
                certificate_configuration: Optional[DistributedAvailabilityGroupCreateUpdateAvailabilityGroupCertificateConfiguration] = ..., 
                failover_mode: Optional[Union[str, ArcSqlServerFailoverMode]] = ..., 
                listener_url: Optional[str] = ..., 
                seeding_mode: Optional[Union[str, SeedingMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DistributedAvailabilityGroupCreateUpdateConfiguration(_Model):
        availability_group_name: Optional[str]
        primary_availability_group: Optional[DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration]
        secondary_availability_group: Optional[DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                availability_group_name: Optional[str] = ..., 
                primary_availability_group: Optional[DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration] = ..., 
                secondary_availability_group: Optional[DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.DtcSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "NONE"
        PER_DB = "PER_DB"


    class azure.mgmt.azurearcdata.models.EditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_INTELLIGENCE = "Business Intelligence"
        DEVELOPER = "Developer"
        ENTERPRISE = "Enterprise"
        EVALUATION = "Evaluation"
        EXPRESS = "Express"
        STANDARD = "Standard"
        STANDARD_DEVELOPER = "Standard Developer"
        UNKNOWN = "Unknown"
        WEB = "Web"


    class azure.mgmt.azurearcdata.models.EncryptionAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AES = "AES"
        AES_RC4 = "AES, RC4"
        NONE = "NONE"
        NONE_AES = "NONE, AES"
        NONE_AES_RC4 = "NONE, AES, RC4"
        NONE_RC4 = "NONE, RC4"
        NONE_RC4_AES = "NONE, RC4, AES"
        RC4 = "RC4"
        RC4_AES = "RC4, AES"


    class azure.mgmt.azurearcdata.models.EntraAuthentication(_Model):
        client_id: Optional[str]
        identity_type: Optional[Union[str, IdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, IdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.azurearcdata.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.azurearcdata.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ExecutionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNNING = "Running"
        WAITING = "Waiting"


    class azure.mgmt.azurearcdata.models.ExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[Union[str, ExtendedLocationTypes]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"


    class azure.mgmt.azurearcdata.models.FailoverCluster(_Model):
        host_ip_addresses: Optional[list[HostIPAddressInformation]]
        host_names: Optional[list[str]]
        id: Optional[str]
        network_name: Optional[str]
        sql_instance_ids: Optional[list[str]]


    class azure.mgmt.azurearcdata.models.FailoverGroupPartnerSyncMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYNC = "async"
        SYNC = "sync"


    class azure.mgmt.azurearcdata.models.FailoverGroupProperties(_Model):
        partner_managed_instance_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        spec: FailoverGroupSpec
        status: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                partner_managed_instance_id: str, 
                spec: FailoverGroupSpec, 
                status: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.FailoverGroupResource(ProxyResource):
        id: str
        name: str
        properties: FailoverGroupProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: FailoverGroupProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.FailoverGroupSpec(_Model):
        partner_mi: Optional[str]
        partner_mirroring_cert: Optional[str]
        partner_mirroring_url: Optional[str]
        partner_sync_mode: Optional[Union[str, FailoverGroupPartnerSyncMode]]
        role: Union[str, InstanceFailoverGroupRole]
        shared_name: Optional[str]
        source_mi: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                partner_mi: Optional[str] = ..., 
                partner_mirroring_cert: Optional[str] = ..., 
                partner_mirroring_url: Optional[str] = ..., 
                partner_sync_mode: Optional[Union[str, FailoverGroupPartnerSyncMode]] = ..., 
                role: Union[str, InstanceFailoverGroupRole], 
                shared_name: Optional[str] = ..., 
                source_mi: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.FailoverMiLinkResourceId(_Model):
        force: Optional[bool]
        managed_instance_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                force: Optional[bool] = ..., 
                managed_instance_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.FailureConditionLevel(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIVE = 5
        FOUR = 4
        ONE = 1
        THREE = 3
        TWO = 2


    class azure.mgmt.azurearcdata.models.HostIPAddressInformation(_Model):
        ip_address: Optional[str]
        subnet_mask: Optional[str]


    class azure.mgmt.azurearcdata.models.HostType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWS_KUBERNETES_SERVICE = "AWS Kubernetes Service"
        AWS_VIRTUAL_MACHINE = "AWS Virtual Machine"
        AWS_VM_WARE_VIRTUAL_MACHINE = "AWS VMWare Virtual Machine"
        AZURE_KUBERNETES_SERVICE = "Azure Kubernetes Service"
        AZURE_VIRTUAL_MACHINE = "Azure Virtual Machine"
        AZURE_VM_WARE_VIRTUAL_MACHINE = "Azure VMWare Virtual Machine"
        CONTAINER = "Container"
        GCP_KUBERNETES_SERVICE = "GCP Kubernetes Service"
        GCP_VIRTUAL_MACHINE = "GCP Virtual Machine"
        GCP_VM_WARE_VIRTUAL_MACHINE = "GCP VMWare Virtual Machine"
        HYPER_V_VIRTUAL_MACHINE = "Hyper-V Virtual Machine"
        OTHER = "Other"
        PHYSICAL_SERVER = "Physical Server"
        VIRTUAL_MACHINE = "Virtual Machine"


    class azure.mgmt.azurearcdata.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"


    class azure.mgmt.azurearcdata.models.ImpactedObjectsInfo(_Model):
        feature_id: Optional[str]
        issue_category: Optional[str]
        number_impacted: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                feature_id: Optional[str] = ..., 
                issue_category: Optional[str] = ..., 
                number_impacted: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ImpactedObjectsSuitabilitySummary(_Model):
        azure_sql_database: Optional[list[ImpactedObjectsInfo]]
        azure_sql_managed_instance: Optional[list[ImpactedObjectsInfo]]


    class azure.mgmt.azurearcdata.models.Infrastructure(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALIBABA = "alibaba"
        AWS = "aws"
        AZURE = "azure"
        GCP = "gcp"
        ONPREMISES = "onpremises"
        OTHER = "other"


    class azure.mgmt.azurearcdata.models.InitiatedFrom(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADS = "ADS"
        AZURE_ARC = "Azure Arc"
        DMS_CLI = "DMS-CLI"
        DMS_PORTAL = "DMS-Portal"
        DMS_PS = "DMS-PS"
        DMS_SDK = "DMS-SDK"
        OTHER = "Other"
        SSMA = "SSMA"
        SSMS = "SSMS"


    class azure.mgmt.azurearcdata.models.InstanceFailoverGroupRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCE_PRIMARY_ALLOW_DATA_LOSS = "force-primary-allow-data-loss"
        FORCE_SECONDARY = "force-secondary"
        PRIMARY = "primary"
        SECONDARY = "secondary"


    class azure.mgmt.azurearcdata.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurearcdata.models.K8SActiveDirectory(_Model):
        account_name: Optional[str]
        connector: Optional[K8SActiveDirectoryConnector]
        encryption_types: Optional[list[str]]
        keytab_secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                connector: Optional[K8SActiveDirectoryConnector] = ..., 
                encryption_types: Optional[list[str]] = ..., 
                keytab_secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8SActiveDirectoryConnector(_Model):
        name: Optional[str]
        namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8SNetworkSettings(_Model):
        forceencryption: Optional[int]
        tlsciphers: Optional[str]
        tlsprotocols: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                forceencryption: Optional[int] = ..., 
                tlsciphers: Optional[str] = ..., 
                tlsprotocols: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8SResourceRequirements(_Model):
        limits: Optional[dict[str, str]]
        requests: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                limits: Optional[dict[str, str]] = ..., 
                requests: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8SScheduling(_Model):
        default: Optional[K8SSchedulingOptions]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[K8SSchedulingOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8SSchedulingOptions(_Model):
        resources: Optional[K8SResourceRequirements]

        @overload
        def __init__(
                self, 
                *, 
                resources: Optional[K8SResourceRequirements] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8SSecurity(_Model):
        active_directory: Optional[K8SActiveDirectory]
        admin_login_secret: Optional[str]
        service_certificate_secret: Optional[str]
        transparent_data_encryption: Optional[K8StransparentDataEncryption]

        @overload
        def __init__(
                self, 
                *, 
                active_directory: Optional[K8SActiveDirectory] = ..., 
                admin_login_secret: Optional[str] = ..., 
                service_certificate_secret: Optional[str] = ..., 
                transparent_data_encryption: Optional[K8StransparentDataEncryption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8SSettings(_Model):
        network: Optional[K8SNetworkSettings]

        @overload
        def __init__(
                self, 
                *, 
                network: Optional[K8SNetworkSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.K8StransparentDataEncryption(_Model):
        mode: Optional[str]
        protector_secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[str] = ..., 
                protector_secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.KeytabInformation(_Model):
        keytab: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                keytab: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.LastExecutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        FAULTED = "Faulted"
        POSTPONED = "Postponed"
        RESCHEDULED = "Rescheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurearcdata.models.LicenseCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CORE = "Core"


    class azure.mgmt.azurearcdata.models.LogAnalyticsWorkspaceConfig(_Model):
        primary_key: Optional[str]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_key: Optional[str] = ..., 
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ManagedInstanceLinkCreateUpdateConfiguration(_Model):
        availability_group: Optional[AvailabilityGroupCreateUpdateConfiguration]
        distributed_availability_group: Optional[DistributedAvailabilityGroupCreateUpdateConfiguration]
        mi_link_configuration: Optional[MiLinkCreateUpdateConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                availability_group: Optional[AvailabilityGroupCreateUpdateConfiguration] = ..., 
                distributed_availability_group: Optional[DistributedAvailabilityGroupCreateUpdateConfiguration] = ..., 
                mi_link_configuration: Optional[MiLinkCreateUpdateConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.MiLinkAssessmentCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOX_TO_MI_NETWORK_CONNECTIVITY = "BoxToMiNetworkConnectivity"
        CERTIFICATES = "Certificates"
        DAG_CROSS_VALIDATION = "DagCrossValidation"
        MANAGED_INSTANCE = "ManagedInstance"
        MANAGED_INSTANCE_CROSS_VALIDATION = "ManagedInstanceCrossValidation"
        MANAGED_INSTANCE_DATABASE = "ManagedInstanceDatabase"
        MI_TO_BOX_NETWORK_CONNECTIVITY = "MiToBoxNetworkConnectivity"
        SQL_INSTANCE = "SqlInstance"
        SQL_INSTANCE_AG = "SqlInstanceAg"
        SQL_INSTANCE_DATABASE = "SqlInstanceDatabase"


    class azure.mgmt.azurearcdata.models.MiLinkCreateUpdateConfiguration(_Model):
        instance_availability_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                instance_availability_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.Migration(_Model):
        assessment: Optional[MigrationAssessment]
        target_resource_id: Optional[str]
        target_selected_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                assessment: Optional[MigrationAssessment] = ..., 
                target_resource_id: Optional[str] = ..., 
                target_selected_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.MigrationAssessment(_Model):
        assessment_upload_time: Optional[datetime]
        assessment_viewed_time: Optional[datetime]
        enabled: Optional[bool]
        impacted_objects_summary: Optional[ImpactedObjectsSuitabilitySummary]
        server_assessments: Optional[list[ServerAssessmentsItem]]
        settings: Optional[MigrationAssessmentSettings]
        sku_recommendation_results: Optional[SkuRecommendationResults]
        target_recommendation_generation_time: Optional[datetime]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_viewed_time: Optional[datetime] = ..., 
                enabled: Optional[bool] = ..., 
                impacted_objects_summary: Optional[ImpactedObjectsSuitabilitySummary] = ..., 
                settings: Optional[MigrationAssessmentSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.MigrationAssessmentSettings(_Model):
        comfort_factor: Optional[int]
        cost_options: Optional[CostOptionSelectedValues]
        currency: Optional[str]
        discount_percentage: Optional[float]
        lookback_period_in_days: Optional[int]
        percentile: Optional[float]
        strategy: Optional[str]
        target_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                comfort_factor: Optional[int] = ..., 
                cost_options: Optional[CostOptionSelectedValues] = ..., 
                currency: Optional[str] = ..., 
                discount_percentage: Optional[float] = ..., 
                lookback_period_in_days: Optional[int] = ..., 
                percentile: Optional[float] = ..., 
                strategy: Optional[str] = ..., 
                target_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.MigrationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGICAL = "Logical"
        LOG_SHIPPING = "LogShipping"
        MI_LINK = "MILink"
        OTHER = "Other"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.MigrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        IN_PROGRESS_WITH_WARNINGS = "InProgressWithWarnings"
        NOT_STARTED = "NotStarted"
        SUCCESSFUL = "Successful"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIXED = "Mixed"
        UNDEFINED = "Undefined"
        WINDOWS = "Windows"


    class azure.mgmt.azurearcdata.models.Monitoring(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.OnPremiseProperty(_Model):
        id: str
        public_signing_key: str
        signing_certificate_thumbprint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                public_signing_key: str, 
                signing_certificate_thumbprint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.Operation(_Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Optional[Union[str, OperationOrigin]]
        properties: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                display: OperationDisplay, 
                is_data_action: bool, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.OperationDisplay(_Model):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"


    class azure.mgmt.azurearcdata.models.PostgresInstance(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: PostgresInstanceProperties
        sku: Optional[PostgresInstanceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: PostgresInstanceProperties, 
                sku: Optional[PostgresInstanceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.PostgresInstanceProperties(_Model):
        admin: Optional[str]
        basic_login_information: Optional[BasicLoginInformation]
        data_controller_id: Optional[str]
        k8_s_raw: Optional[Any]
        last_uploaded_date: Optional[datetime]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin: Optional[str] = ..., 
                basic_login_information: Optional[BasicLoginInformation] = ..., 
                data_controller_id: Optional[str] = ..., 
                k8_s_raw: Optional[Any] = ..., 
                last_uploaded_date: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.PostgresInstanceSku(CommonSku):
        capacity: int
        dev: bool
        family: str
        name: str
        size: str
        tier: Optional[Literal["Hyperscale"]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                dev: Optional[bool] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Literal[Hyperscale]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.PostgresInstanceUpdate(_Model):
        properties: Optional[PostgresInstanceProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PostgresInstanceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.PrimaryAllowConnections(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "ALL"
        READ_WRITE = "READ_WRITE"


    class azure.mgmt.azurearcdata.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurearcdata.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurearcdata.models.RecommendationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_READY = "NotReady"
        READY = "Ready"
        READY_WITH_CONDITIONS = "ReadyWithConditions"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.RecoveryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BULK_LOGGED = "Bulk-logged"
        FULL = "Full"
        SIMPLE = "Simple"


    class azure.mgmt.azurearcdata.models.ReplicationPartnerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SQLVM = "AzureSQLVM"
        AZURE_SQL_MANAGED_INSTANCE = "AzureSQLManagedInstance"
        SQL_SERVER = "SQLServer"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.azurearcdata.models.ResourceUpdateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SKIP_RESOURCE_UPDATE = "SkipResourceUpdate"
        UPDATE_ALL_TARGET_RECOMMENDATION_DETAILS = "UpdateAllTargetRecommendationDetails"


    class azure.mgmt.azurearcdata.models.Result(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        NOT_COMPLETED = "NotCompleted"
        SKIPPED = "Skipped"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"


    class azure.mgmt.azurearcdata.models.Role(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "ALL"
        NONE = "NONE"
        PARTNER = "PARTNER"
        WITNESS = "WITNESS"


    class azure.mgmt.azurearcdata.models.Schedule(_Model):
        cron_trigger: Optional[CronTrigger]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cron_trigger: Optional[CronTrigger] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE_GROUP = "ResourceGroup"
        SUBSCRIPTION = "Subscription"
        TENANT = "Tenant"


    class azure.mgmt.azurearcdata.models.SecondaryAllowConnections(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "ALL"
        NO = "NO"
        READ_ONLY = "READ_ONLY"


    class azure.mgmt.azurearcdata.models.SeedingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "AUTOMATIC"
        MANUAL = "MANUAL"


    class azure.mgmt.azurearcdata.models.SequencerAction(_Model):
        action_id: Optional[str]
        result: Optional[Union[str, Result]]
        state: Optional[Union[str, SequencerState]]

        @overload
        def __init__(
                self, 
                *, 
                action_id: Optional[str] = ..., 
                result: Optional[Union[str, Result]] = ..., 
                state: Optional[Union[str, SequencerState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SequencerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        CREATING_SUCCESSORS = "CreatingSuccessors"
        EXECUTING_ACTION = "ExecutingAction"
        NOT_STARTED = "NotStarted"
        WAITING_PREDECESSORS = "WaitingPredecessors"


    class azure.mgmt.azurearcdata.models.ServerAssessmentsItem(_Model):
        applies_to_migration_target_platform: Optional[str]
        feature_id: Optional[str]
        impacted_objects: Optional[list[ServerAssessmentsPropertiesItemsItem]]
        issue_category: Optional[str]
        more_information: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                applies_to_migration_target_platform: Optional[str] = ..., 
                feature_id: Optional[str] = ..., 
                impacted_objects: Optional[list[ServerAssessmentsPropertiesItemsItem]] = ..., 
                issue_category: Optional[str] = ..., 
                more_information: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ServerAssessmentsPropertiesItemsItem(_Model):
        impact_detail: Optional[str]
        name: Optional[str]
        object_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                impact_detail: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.ServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENGINE = "Engine"
        PBIRS = "PBIRS"
        SSAS = "SSAS"
        SSIS = "SSIS"
        SSRS = "SSRS"


    class azure.mgmt.azurearcdata.models.SkuRecommendationResults(_Model):
        azure_sql_database: Optional[SkuRecommendationResultsAzureSqlDatabase]
        azure_sql_managed_instance: Optional[SkuRecommendationResultsAzureSqlManagedInstance]
        azure_sql_virtual_machine: Optional[SkuRecommendationResultsAzureSqlVirtualMachine]

        @overload
        def __init__(
                self, 
                *, 
                azure_sql_database: Optional[SkuRecommendationResultsAzureSqlDatabase] = ..., 
                azure_sql_managed_instance: Optional[SkuRecommendationResultsAzureSqlManagedInstance] = ..., 
                azure_sql_virtual_machine: Optional[SkuRecommendationResultsAzureSqlVirtualMachine] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlDatabase(_Model):
        monthly_cost: Optional[SkuRecommendationResultsMonthlyCost]
        monthly_cost_options: Optional[list[SkuRecommendationResultsMonthlyCostOptionItem]]
        number_of_server_blocker_issues: Optional[int]
        recommendation_status: Optional[Union[str, RecommendationStatus]]
        target_sku: Optional[SkuRecommendationResultsAzureSqlDatabaseTargetSku]

        @overload
        def __init__(
                self, 
                *, 
                monthly_cost: Optional[SkuRecommendationResultsMonthlyCost] = ..., 
                number_of_server_blocker_issues: Optional[int] = ..., 
                recommendation_status: Optional[Union[str, RecommendationStatus]] = ..., 
                target_sku: Optional[SkuRecommendationResultsAzureSqlDatabaseTargetSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlDatabaseTargetSku(_Model):
        category: Optional[SkuRecommendationResultsAzureSqlDatabaseTargetSkuCategory]
        compute_size: Optional[int]
        max_storage_iops: Optional[float]
        max_throughput_m_bps: Optional[float]
        predicted_data_size_in_mb: Optional[float]
        predicted_log_size_in_mb: Optional[float]
        storage_max_size_in_mb: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[SkuRecommendationResultsAzureSqlDatabaseTargetSkuCategory] = ..., 
                compute_size: Optional[int] = ..., 
                max_storage_iops: Optional[float] = ..., 
                max_throughput_m_bps: Optional[float] = ..., 
                predicted_data_size_in_mb: Optional[float] = ..., 
                predicted_log_size_in_mb: Optional[float] = ..., 
                storage_max_size_in_mb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlDatabaseTargetSkuCategory(_Model):
        compute_tier: Optional[str]
        hardware_type: Optional[str]
        sql_purchasing_model: Optional[str]
        sql_service_tier: Optional[str]
        zone_redundancy_available: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                compute_tier: Optional[str] = ..., 
                hardware_type: Optional[str] = ..., 
                sql_purchasing_model: Optional[str] = ..., 
                sql_service_tier: Optional[str] = ..., 
                zone_redundancy_available: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlManagedInstance(_Model):
        monthly_cost: Optional[SkuRecommendationResultsMonthlyCost]
        monthly_cost_options: Optional[list[SkuRecommendationResultsMonthlyCostOptionItem]]
        number_of_server_blocker_issues: Optional[int]
        recommendation_status: Optional[Union[str, RecommendationStatus]]
        target_sku: Optional[SkuRecommendationResultsAzureSqlManagedInstanceTargetSku]

        @overload
        def __init__(
                self, 
                *, 
                monthly_cost: Optional[SkuRecommendationResultsMonthlyCost] = ..., 
                number_of_server_blocker_issues: Optional[int] = ..., 
                recommendation_status: Optional[Union[str, RecommendationStatus]] = ..., 
                target_sku: Optional[SkuRecommendationResultsAzureSqlManagedInstanceTargetSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlManagedInstanceTargetSku(_Model):
        category: Optional[SkuRecommendationResultsAzureSqlManagedInstanceTargetSkuCategory]
        compute_size: Optional[int]
        max_storage_iops: Optional[float]
        max_throughput_m_bps: Optional[float]
        predicted_data_size_in_mb: Optional[float]
        predicted_log_size_in_mb: Optional[float]
        storage_max_size_in_mb: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[SkuRecommendationResultsAzureSqlManagedInstanceTargetSkuCategory] = ..., 
                compute_size: Optional[int] = ..., 
                max_storage_iops: Optional[float] = ..., 
                max_throughput_m_bps: Optional[float] = ..., 
                predicted_data_size_in_mb: Optional[float] = ..., 
                predicted_log_size_in_mb: Optional[float] = ..., 
                storage_max_size_in_mb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlManagedInstanceTargetSkuCategory(_Model):
        compute_tier: Optional[str]
        hardware_type: Optional[str]
        sql_purchasing_model: Optional[str]
        sql_service_tier: Optional[str]
        zone_redundancy_available: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                compute_tier: Optional[str] = ..., 
                hardware_type: Optional[str] = ..., 
                sql_purchasing_model: Optional[str] = ..., 
                sql_service_tier: Optional[str] = ..., 
                zone_redundancy_available: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlVirtualMachine(_Model):
        monthly_cost: Optional[SkuRecommendationResultsMonthlyCost]
        monthly_cost_options: Optional[list[SkuRecommendationResultsMonthlyCostOptionItem]]
        number_of_server_blocker_issues: Optional[int]
        recommendation_status: Optional[Union[str, RecommendationStatus]]
        target_sku: Optional[SkuRecommendationResultsAzureSqlVirtualMachineTargetSku]

        @overload
        def __init__(
                self, 
                *, 
                monthly_cost: Optional[SkuRecommendationResultsMonthlyCost] = ..., 
                number_of_server_blocker_issues: Optional[int] = ..., 
                recommendation_status: Optional[Union[str, RecommendationStatus]] = ..., 
                target_sku: Optional[SkuRecommendationResultsAzureSqlVirtualMachineTargetSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlVirtualMachineTargetSku(_Model):
        category: Optional[SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuCategory]
        compute_size: Optional[int]
        data_disk_sizes: Optional[list[DiskSizes]]
        log_disk_sizes: Optional[list[DiskSizes]]
        predicted_data_size_in_mb: Optional[float]
        predicted_log_size_in_mb: Optional[float]
        temp_db_disk_sizes: Optional[list[DiskSizes]]
        virtual_machine_size: Optional[SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuVirtualMachineSize]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuCategory] = ..., 
                compute_size: Optional[int] = ..., 
                data_disk_sizes: Optional[list[DiskSizes]] = ..., 
                log_disk_sizes: Optional[list[DiskSizes]] = ..., 
                predicted_data_size_in_mb: Optional[float] = ..., 
                predicted_log_size_in_mb: Optional[float] = ..., 
                temp_db_disk_sizes: Optional[list[DiskSizes]] = ..., 
                virtual_machine_size: Optional[SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuVirtualMachineSize] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuCategory(_Model):
        available_vm_skus: Optional[list[str]]
        virtual_machine_family: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                available_vm_skus: Optional[list[str]] = ..., 
                virtual_machine_family: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuVirtualMachineSize(_Model):
        azure_sku_name: Optional[str]
        compute_size: Optional[int]
        max_network_interfaces: Optional[int]
        size_name: Optional[str]
        v_cpus_available: Optional[int]
        virtual_machine_family: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_sku_name: Optional[str] = ..., 
                compute_size: Optional[int] = ..., 
                max_network_interfaces: Optional[int] = ..., 
                size_name: Optional[str] = ..., 
                v_cpus_available: Optional[int] = ..., 
                virtual_machine_family: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsMonthlyCost(_Model):
        compute_cost: Optional[float]
        iops_cost: Optional[float]
        sql_license_cost: Optional[float]
        storage_cost: Optional[float]
        total_cost: Optional[float]
        windows_license_cost: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                compute_cost: Optional[float] = ..., 
                iops_cost: Optional[float] = ..., 
                sql_license_cost: Optional[float] = ..., 
                storage_cost: Optional[float] = ..., 
                total_cost: Optional[float] = ..., 
                windows_license_cost: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationResultsMonthlyCostOptionItem(_Model):
        key_name: Optional[str]
        key_value: Optional[CostTypeValues]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_value: Optional[CostTypeValues] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationSummary(_Model):
        impacted_objects_summary: Optional[list[ImpactedObjectsInfo]]
        monthly_cost: Optional[SkuRecommendationResultsMonthlyCost]
        monthly_cost_options: Optional[list[SkuRecommendationResultsMonthlyCostOptionItem]]
        num_of_blocker_issues: Optional[int]
        recommendation_status: Optional[Union[str, RecommendationStatus]]
        target_sku: Optional[SkuRecommendationSummaryTargetSku]

        @overload
        def __init__(
                self, 
                *, 
                monthly_cost: Optional[SkuRecommendationResultsMonthlyCost] = ..., 
                num_of_blocker_issues: Optional[int] = ..., 
                recommendation_status: Optional[Union[str, RecommendationStatus]] = ..., 
                target_sku: Optional[SkuRecommendationSummaryTargetSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationSummaryTargetSku(_Model):
        category: Optional[SkuRecommendationSummaryTargetSkuCategory]
        compute_size: Optional[int]
        max_storage_iops: Optional[float]
        max_throughput_m_bps: Optional[float]
        predicted_data_size_in_mb: Optional[float]
        predicted_log_size_in_mb: Optional[float]
        storage_max_size_in_mb: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[SkuRecommendationSummaryTargetSkuCategory] = ..., 
                compute_size: Optional[int] = ..., 
                max_storage_iops: Optional[float] = ..., 
                max_throughput_m_bps: Optional[float] = ..., 
                predicted_data_size_in_mb: Optional[float] = ..., 
                predicted_log_size_in_mb: Optional[float] = ..., 
                storage_max_size_in_mb: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SkuRecommendationSummaryTargetSkuCategory(_Model):
        compute_tier: Optional[str]
        hardware_type: Optional[str]
        sql_purchasing_model: Optional[str]
        sql_service_tier: Optional[str]
        zone_redundancy_available: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                compute_tier: Optional[str] = ..., 
                hardware_type: Optional[str] = ..., 
                sql_purchasing_model: Optional[str] = ..., 
                sql_service_tier: Optional[str] = ..., 
                zone_redundancy_available: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlAvailabilityGroupDatabaseReplicaResourceProperties(_Model):
        database_name: Optional[str]
        database_state_description: Optional[str]
        is_commit_participant: Optional[bool]
        is_local: Optional[bool]
        is_primary_replica: Optional[bool]
        is_suspended: Optional[bool]
        replica_name: Optional[str]
        suspend_reason_description: Optional[str]
        synchronization_health_description: Optional[str]
        synchronization_state_description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem(_Model):
        ip_address: Optional[str]
        mask: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                mask: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlAvailabilityGroupReplicaResourceProperties(_Model):
        configure: Optional[AvailabilityGroupConfigure]
        replica_id: Optional[str]
        replica_name: Optional[str]
        replica_resource_id: Optional[str]
        state: Optional[AvailabilityGroupState]

        @overload
        def __init__(
                self, 
                *, 
                configure: Optional[AvailabilityGroupConfigure] = ..., 
                replica_name: Optional[str] = ..., 
                replica_resource_id: Optional[str] = ..., 
                state: Optional[AvailabilityGroupState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlAvailabilityGroupStaticIPListenerProperties(_Model):
        dns_name: Optional[str]
        ip_v4_addresses_and_masks: Optional[list[SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem]]
        ip_v6_addresses: Optional[list[str]]
        port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                dns_name: Optional[str] = ..., 
                ip_v4_addresses_and_masks: Optional[list[SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem]] = ..., 
                ip_v6_addresses: Optional[list[str]] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlManagedInstance(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: SqlManagedInstanceProperties
        sku: Optional[SqlManagedInstanceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: SqlManagedInstanceProperties, 
                sku: Optional[SqlManagedInstanceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceK8SRaw(_Model):
        spec: Optional[SqlManagedInstanceK8SSpec]

        @overload
        def __init__(
                self, 
                *, 
                spec: Optional[SqlManagedInstanceK8SSpec] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceK8SSpec(_Model):
        replicas: Optional[int]
        scheduling: Optional[K8SScheduling]
        security: Optional[K8SSecurity]
        settings: Optional[K8SSettings]

        @overload
        def __init__(
                self, 
                *, 
                replicas: Optional[int] = ..., 
                scheduling: Optional[K8SScheduling] = ..., 
                security: Optional[K8SSecurity] = ..., 
                settings: Optional[K8SSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceProperties(_Model):
        active_directory_information: Optional[ActiveDirectoryInformation]
        admin: Optional[str]
        basic_login_information: Optional[BasicLoginInformation]
        cluster_id: Optional[str]
        data_controller_id: Optional[str]
        end_time: Optional[str]
        extension_id: Optional[str]
        k8_s_raw: Optional[SqlManagedInstanceK8SRaw]
        last_uploaded_date: Optional[datetime]
        license_type: Optional[Union[str, ArcSqlManagedInstanceLicenseType]]
        provisioning_state: Optional[str]
        start_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_directory_information: Optional[ActiveDirectoryInformation] = ..., 
                admin: Optional[str] = ..., 
                basic_login_information: Optional[BasicLoginInformation] = ..., 
                cluster_id: Optional[str] = ..., 
                data_controller_id: Optional[str] = ..., 
                end_time: Optional[str] = ..., 
                extension_id: Optional[str] = ..., 
                k8_s_raw: Optional[SqlManagedInstanceK8SRaw] = ..., 
                last_uploaded_date: Optional[datetime] = ..., 
                license_type: Optional[Union[str, ArcSqlManagedInstanceLicenseType]] = ..., 
                start_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceSku(_Model):
        capacity: Optional[int]
        dev: Optional[bool]
        family: Optional[str]
        name: Literal["vCore"]
        size: Optional[str]
        tier: Optional[Union[str, SqlManagedInstanceSkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                dev: Optional[bool] = ..., 
                family: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SqlManagedInstanceSkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CRITICAL = "BusinessCritical"
        GENERAL_PURPOSE = "GeneralPurpose"


    class azure.mgmt.azurearcdata.models.SqlManagedInstanceUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerAvailabilityGroupResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: SqlServerAvailabilityGroupResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: SqlServerAvailabilityGroupResourceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerAvailabilityGroupResourceProperties(_Model):
        availability_group_id: Optional[str]
        collection_timestamp: Optional[datetime]
        databases: Optional[SqlServerAvailabilityGroupResourcePropertiesDatabases]
        info: Optional[AvailabilityGroupInfo]
        instance_name: Optional[str]
        provisioning_state: Optional[str]
        replicas: Optional[SqlServerAvailabilityGroupResourcePropertiesReplicas]
        server_name: Optional[str]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                databases: Optional[SqlServerAvailabilityGroupResourcePropertiesDatabases] = ..., 
                info: Optional[AvailabilityGroupInfo] = ..., 
                replicas: Optional[SqlServerAvailabilityGroupResourcePropertiesReplicas] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerAvailabilityGroupResourcePropertiesDatabases(_Model):
        next_link: Optional[str]
        value: Optional[list[SqlAvailabilityGroupDatabaseReplicaResourceProperties]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SqlAvailabilityGroupDatabaseReplicaResourceProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerAvailabilityGroupResourcePropertiesReplicas(_Model):
        next_link: Optional[str]
        value: Optional[list[SqlAvailabilityGroupReplicaResourceProperties]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SqlAvailabilityGroupReplicaResourceProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerAvailabilityGroupUpdate(_Model):
        properties: Optional[SqlServerAvailabilityGroupResourceProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlServerAvailabilityGroupResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerDatabaseResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: SqlServerDatabaseResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: SqlServerDatabaseResourceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerDatabaseResourceProperties(_Model):
        backup_information: Optional[SqlServerDatabaseResourcePropertiesBackupInformation]
        backup_policy: Optional[BackupPolicy]
        collation_name: Optional[str]
        compatibility_level: Optional[int]
        create_mode: Optional[Union[str, DatabaseCreateMode]]
        data_file_size_mb: Optional[float]
        database_creation_date: Optional[datetime]
        database_options: Optional[SqlServerDatabaseResourcePropertiesDatabaseOptions]
        earliest_restore_date: Optional[datetime]
        is_read_only: Optional[bool]
        last_database_upload_time: Optional[datetime]
        log_file_size_mb: Optional[float]
        migration: Optional[DataBaseMigration]
        provisioning_state: Optional[str]
        recovery_mode: Optional[Union[str, RecoveryMode]]
        restore_point_in_time: Optional[datetime]
        size_mb: Optional[float]
        source_database_id: Optional[str]
        space_available_mb: Optional[float]
        state: Optional[Union[str, DatabaseState]]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_information: Optional[SqlServerDatabaseResourcePropertiesBackupInformation] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                collation_name: Optional[str] = ..., 
                compatibility_level: Optional[int] = ..., 
                create_mode: Optional[Union[str, DatabaseCreateMode]] = ..., 
                data_file_size_mb: Optional[float] = ..., 
                database_creation_date: Optional[datetime] = ..., 
                database_options: Optional[SqlServerDatabaseResourcePropertiesDatabaseOptions] = ..., 
                is_read_only: Optional[bool] = ..., 
                log_file_size_mb: Optional[float] = ..., 
                migration: Optional[DataBaseMigration] = ..., 
                recovery_mode: Optional[Union[str, RecoveryMode]] = ..., 
                restore_point_in_time: Optional[datetime] = ..., 
                size_mb: Optional[float] = ..., 
                source_database_id: Optional[str] = ..., 
                space_available_mb: Optional[float] = ..., 
                state: Optional[Union[str, DatabaseState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerDatabaseResourcePropertiesBackupInformation(_Model):
        last_full_backup: Optional[datetime]
        last_log_backup: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                last_full_backup: Optional[datetime] = ..., 
                last_log_backup: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerDatabaseResourcePropertiesDatabaseOptions(_Model):
        is_auto_close_on: Optional[bool]
        is_auto_create_stats_on: Optional[bool]
        is_auto_shrink_on: Optional[bool]
        is_auto_update_stats_on: Optional[bool]
        is_encrypted: Optional[bool]
        is_hekaton_files_on: Optional[bool]
        is_memory_optimization_enabled: Optional[bool]
        is_remote_data_archive_enabled: Optional[bool]
        is_trustworthy_on: Optional[bool]
        number_of_hekaton_files: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                is_auto_close_on: Optional[bool] = ..., 
                is_auto_create_stats_on: Optional[bool] = ..., 
                is_auto_shrink_on: Optional[bool] = ..., 
                is_auto_update_stats_on: Optional[bool] = ..., 
                is_encrypted: Optional[bool] = ..., 
                is_hekaton_files_on: Optional[bool] = ..., 
                is_memory_optimization_enabled: Optional[bool] = ..., 
                is_remote_data_archive_enabled: Optional[bool] = ..., 
                is_trustworthy_on: Optional[bool] = ..., 
                number_of_hekaton_files: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerDatabaseUpdate(_Model):
        properties: Optional[SqlServerDatabaseResourceProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlServerDatabaseResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerEsuLicense(TrackedResource):
        id: str
        location: str
        name: str
        properties: SqlServerEsuLicenseProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: SqlServerEsuLicenseProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerEsuLicenseProperties(_Model):
        activated_at: Optional[datetime]
        activation_state: Union[str, State]
        billing_plan: Union[str, BillingPlan]
        physical_cores: int
        scope_type: Union[str, ScopeType]
        tenant_id: Optional[str]
        terminated_at: Optional[datetime]
        unique_id: Optional[str]
        version: Union[str, Version]

        @overload
        def __init__(
                self, 
                *, 
                activation_state: Union[str, State], 
                billing_plan: Union[str, BillingPlan], 
                physical_cores: int, 
                scope_type: Union[str, ScopeType], 
                version: Union[str, Version]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerEsuLicenseUpdate(_Model):
        properties: Optional[SqlServerEsuLicenseUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlServerEsuLicenseUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerEsuLicenseUpdateProperties(_Model):
        activated_at: Optional[datetime]
        activation_state: Optional[Union[str, State]]
        billing_plan: Optional[Union[str, BillingPlan]]
        physical_cores: Optional[int]
        scope_type: Optional[Union[str, ScopeType]]
        tenant_id: Optional[str]
        terminated_at: Optional[datetime]
        unique_id: Optional[str]
        version: Optional[Union[str, Version]]

        @overload
        def __init__(
                self, 
                *, 
                activation_state: Optional[Union[str, State]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                physical_cores: Optional[int] = ..., 
                scope_type: Optional[Union[str, ScopeType]] = ..., 
                version: Optional[Union[str, Version]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstance(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SqlServerInstanceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SqlServerInstanceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceBpaColumn(_Model):
        name: Optional[str]
        type: Optional[Union[str, SqlServerInstanceBpaColumnType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, SqlServerInstanceBpaColumnType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceBpaColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "bool"
        DATETIME = "datetime"
        DOUBLE = "double"
        GUID = "guid"
        INT = "int"
        LONG = "long"
        STRING = "string"
        TIMESPAN = "timespan"


    class azure.mgmt.azurearcdata.models.SqlServerInstanceBpaQueryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        HISTORICAL_TRENDS = "HistoricalTrends"


    class azure.mgmt.azurearcdata.models.SqlServerInstanceBpaReportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSESSMENT_DATA_POINT = "AssessmentDataPoint"
        ASSESSMENT_SUMMARY = "AssessmentSummary"


    class azure.mgmt.azurearcdata.models.SqlServerInstanceBpaRequest(_Model):
        query_type: Optional[Union[str, SqlServerInstanceBpaQueryType]]
        report_id: Optional[str]
        report_type: Optional[Union[str, SqlServerInstanceBpaReportType]]
        skip_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                query_type: Optional[Union[str, SqlServerInstanceBpaQueryType]] = ..., 
                report_id: Optional[str] = ..., 
                report_type: Optional[Union[str, SqlServerInstanceBpaReportType]] = ..., 
                skip_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceJob(_Model):
        background_job: Optional[BackgroundJob]
        id: Optional[str]
        instance_name: Optional[str]
        job_exception: Optional[str]
        job_status: Optional[Union[str, JobStatus]]
        sequencer_actions: Optional[list[SequencerAction]]

        @overload
        def __init__(
                self, 
                *, 
                background_job: Optional[BackgroundJob] = ..., 
                id: Optional[str] = ..., 
                instance_name: Optional[str] = ..., 
                job_exception: Optional[str] = ..., 
                job_status: Optional[Union[str, JobStatus]] = ..., 
                sequencer_actions: Optional[list[SequencerAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceJobStatus(_Model):
        background_job: Optional[BackgroundJob]
        id: Optional[str]
        instance_name: Optional[str]
        job_exception: Optional[str]
        job_status: Optional[Union[str, JobStatus]]
        sequencer_actions: Optional[list[SequencerAction]]

        @overload
        def __init__(
                self, 
                *, 
                background_job: Optional[BackgroundJob] = ..., 
                id: Optional[str] = ..., 
                instance_name: Optional[str] = ..., 
                job_exception: Optional[str] = ..., 
                job_status: Optional[Union[str, JobStatus]] = ..., 
                sequencer_actions: Optional[list[SequencerAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceJobsRequest(_Model):
        feature_name: Optional[str]
        job_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                feature_name: Optional[str] = ..., 
                job_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceJobsResponse(_Model):
        jobs: Optional[list[SqlServerInstanceJob]]

        @overload
        def __init__(
                self, 
                *, 
                jobs: Optional[list[SqlServerInstanceJob]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceJobsStatusRequest(_Model):
        feature_name: Optional[str]
        job_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                feature_name: Optional[str] = ..., 
                job_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceJobsStatusResponse(_Model):
        jobs_status: Optional[list[SqlServerInstanceJobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                jobs_status: Optional[list[SqlServerInstanceJobStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceManagedInstanceLinkAssessment(_Model):
        additional_information: Optional[str]
        category: Optional[Union[str, MiLinkAssessmentCategory]]
        failing_dbs: Optional[list[str]]
        information: Optional[str]
        name: Optional[str]
        status: Optional[Union[str, AssessmentStatus]]

        @overload
        def __init__(
                self, 
                *, 
                additional_information: Optional[str] = ..., 
                category: Optional[Union[str, MiLinkAssessmentCategory]] = ..., 
                failing_dbs: Optional[list[str]] = ..., 
                information: Optional[str] = ..., 
                name: Optional[str] = ..., 
                status: Optional[Union[str, AssessmentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceManagedInstanceLinkAssessmentRequest(_Model):
        assessment_categories: Optional[list[Union[str, MiLinkAssessmentCategory]]]
        availability_group_name: str
        azure_managed_instance_resource_id: str
        azure_managed_instance_role: Optional[Union[str, AzureManagedInstanceRole]]
        database_names: list[str]
        distributed_availability_group_name: str
        sql_server_ip_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_categories: Optional[list[Union[str, MiLinkAssessmentCategory]]] = ..., 
                availability_group_name: str, 
                azure_managed_instance_resource_id: str, 
                azure_managed_instance_role: Optional[Union[str, AzureManagedInstanceRole]] = ..., 
                database_names: list[str], 
                distributed_availability_group_name: str, 
                sql_server_ip_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceManagedInstanceLinkAssessmentResponse(_Model):
        assessments: Optional[list[SqlServerInstanceManagedInstanceLinkAssessment]]

        @overload
        def __init__(
                self, 
                *, 
                assessments: Optional[list[SqlServerInstanceManagedInstanceLinkAssessment]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceMigrationReadinessReportResponse(_Model):
        created_time: Optional[datetime]
        is_compressed: Optional[bool]
        report: Optional[str]


    class azure.mgmt.azurearcdata.models.SqlServerInstanceProperties(_Model):
        always_on_role: Optional[Union[str, AlwaysOnRole]]
        authentication: Optional[Authentication]
        azure_defender_status: Optional[Union[str, DefenderStatus]]
        azure_defender_status_last_updated: Optional[datetime]
        backup_policy: Optional[BackupPolicy]
        best_practices_assessment: Optional[BestPracticesAssessment]
        client_connection: Optional[ClientConnection]
        collation: Optional[str]
        container_resource_id: Optional[str]
        cores: Optional[str]
        create_time: Optional[str]
        current_version: Optional[str]
        database_mirroring_endpoint: Optional[DBMEndpoint]
        db_master_key_exists: Optional[bool]
        discovery_source: Optional[Union[str, DiscoverySource]]
        edition: Optional[Union[str, EditionType]]
        failover_cluster: Optional[FailoverCluster]
        host_type: Optional[Union[str, HostType]]
        instance_name: Optional[str]
        is_digi_cert_pki_cert_trust_configured: Optional[bool]
        is_hadr_enabled: Optional[bool]
        is_microsoft_pki_cert_trust_configured: Optional[bool]
        last_inventory_upload_time: Optional[datetime]
        last_usage_upload_time: Optional[datetime]
        license_type: Optional[Union[str, ArcSqlServerLicenseType]]
        max_server_memory_mb: Optional[int]
        migration: Optional[Migration]
        monitoring: Optional[Monitoring]
        patch_level: Optional[str]
        product_id: Optional[str]
        provisioning_state: Optional[str]
        service_type: Optional[Union[str, ServiceType]]
        status: Optional[Union[str, ConnectionStatus]]
        tcp_dynamic_ports: Optional[str]
        tcp_static_ports: Optional[str]
        trace_flags: Optional[list[int]]
        upgrade_locked_until: Optional[datetime]
        v_core: Optional[str]
        version: Optional[Union[str, SqlVersion]]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[Authentication] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                best_practices_assessment: Optional[BestPracticesAssessment] = ..., 
                client_connection: Optional[ClientConnection] = ..., 
                cores: Optional[str] = ..., 
                database_mirroring_endpoint: Optional[DBMEndpoint] = ..., 
                discovery_source: Optional[Union[str, DiscoverySource]] = ..., 
                edition: Optional[Union[str, EditionType]] = ..., 
                failover_cluster: Optional[FailoverCluster] = ..., 
                host_type: Optional[Union[str, HostType]] = ..., 
                instance_name: Optional[str] = ..., 
                migration: Optional[Migration] = ..., 
                monitoring: Optional[Monitoring] = ..., 
                service_type: Optional[Union[str, ServiceType]] = ..., 
                upgrade_locked_until: Optional[datetime] = ..., 
                version: Optional[Union[str, SqlVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceRunBestPracticesAssessmentResponse(_Model):
        background_job: Optional[BackgroundJob]
        id: Optional[str]
        instance_name: Optional[str]
        job_exception: Optional[str]
        job_status: Optional[Union[str, JobStatus]]
        sequencer_actions: Optional[list[SequencerAction]]

        @overload
        def __init__(
                self, 
                *, 
                background_job: Optional[BackgroundJob] = ..., 
                id: Optional[str] = ..., 
                instance_name: Optional[str] = ..., 
                job_exception: Optional[str] = ..., 
                job_status: Optional[Union[str, JobStatus]] = ..., 
                sequencer_actions: Optional[list[SequencerAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceRunMigrationAssessmentResponse(_Model):
        background_job: Optional[BackgroundJob]
        id: Optional[str]
        instance_name: Optional[str]
        job_exception: Optional[str]
        job_status: Optional[Union[str, JobStatus]]
        sequencer_actions: Optional[list[SequencerAction]]

        @overload
        def __init__(
                self, 
                *, 
                background_job: Optional[BackgroundJob] = ..., 
                id: Optional[str] = ..., 
                instance_name: Optional[str] = ..., 
                job_exception: Optional[str] = ..., 
                job_status: Optional[Union[str, JobStatus]] = ..., 
                sequencer_actions: Optional[list[SequencerAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceRunMigrationReadinessAssessmentResponse(_Model):
        background_job: Optional[BackgroundJob]
        id: Optional[str]
        instance_name: Optional[str]
        job_exception: Optional[str]
        job_status: Optional[Union[str, JobStatus]]
        sequencer_actions: Optional[list[SequencerAction]]

        @overload
        def __init__(
                self, 
                *, 
                background_job: Optional[BackgroundJob] = ..., 
                id: Optional[str] = ..., 
                instance_name: Optional[str] = ..., 
                job_exception: Optional[str] = ..., 
                job_status: Optional[Union[str, JobStatus]] = ..., 
                sequencer_actions: Optional[list[SequencerAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceRunTargetRecommendationJobRequest(_Model):
        include_file_level_requirements: Optional[bool]
        lookback_period_in_days: Optional[int]
        percentile: Optional[int]
        resource_update_mode: Optional[Union[str, ResourceUpdateMode]]
        target_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                include_file_level_requirements: Optional[bool] = ..., 
                lookback_period_in_days: Optional[int] = ..., 
                percentile: Optional[int] = ..., 
                resource_update_mode: Optional[Union[str, ResourceUpdateMode]] = ..., 
                target_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceRunTargetRecommendationJobResponse(_Model):
        job_status: Optional[Union[str, JobStatus]]


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTargetRecommendationReport(_Model):
        created_time: Optional[datetime]
        report_id: Optional[str]
        sections: Optional[list[SqlServerInstanceTargetRecommendationReportSection]]


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTargetRecommendationReportSection(_Model):
        data: Optional[str]
        database_name: Optional[str]
        is_compressed: Optional[bool]
        type: Optional[Union[str, SqlServerInstanceTargetRecommendationReportSectionType]]


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTargetRecommendationReportSectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_REQUIREMENTS_PER_DATABASE = "FileRequirementsPerDatabase"
        REQUIREMENTS_PER_DATABASE = "RequirementsPerDatabase"
        REQUIREMENTS_PER_INSTANCE = "RequirementsPerInstance"
        SQL_DB_TARGET_RECOMMENDATION_PER_DATABASE = "SqlDbTargetRecommendationPerDatabase"
        SQL_MI_TARGET_RECOMMENDATION_PER_INSTANCE = "SqlMiTargetRecommendationPerInstance"
        SQL_VM_TARGET_RECOMMENDATION_PER_INSTANCE = "SqlVmTargetRecommendationPerInstance"


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTargetRecommendationReportsRequest(_Model):
        database_names: Optional[list[str]]
        report_offset: Optional[int]
        section_offset: Optional[int]
        section_type: Optional[Union[str, SqlServerInstanceTargetRecommendationReportSectionType]]

        @overload
        def __init__(
                self, 
                *, 
                database_names: Optional[list[str]] = ..., 
                report_offset: Optional[int] = ..., 
                section_offset: Optional[int] = ..., 
                section_type: Optional[Union[str, SqlServerInstanceTargetRecommendationReportSectionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTargetRecommendationReportsResponse(_Model):
        job_status: Optional[Union[str, JobStatus]]
        next_report_offset: Optional[int]
        next_section_offset: Optional[int]
        reports: Optional[list[SqlServerInstanceTargetRecommendationReport]]
        total_report_count: Optional[int]


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTelemetryColumn(_Model):
        name: Optional[str]
        type: Optional[Union[str, SqlServerInstanceTelemetryColumnType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, SqlServerInstanceTelemetryColumnType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTelemetryColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "bool"
        DATETIME = "datetime"
        DOUBLE = "double"
        GUID = "guid"
        INT = "int"
        LONG = "long"
        STRING = "string"
        TIMESPAN = "timespan"


    class azure.mgmt.azurearcdata.models.SqlServerInstanceTelemetryRequest(_Model):
        aggregation_type: Optional[Union[str, AggregationType]]
        database_names: Optional[list[str]]
        dataset_name: str
        end_time: Optional[datetime]
        interval: Optional[timedelta]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[Union[str, AggregationType]] = ..., 
                database_names: Optional[list[str]] = ..., 
                dataset_name: str, 
                end_time: Optional[datetime] = ..., 
                interval: Optional[timedelta] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceUpdate(_Model):
        properties: Optional[SqlServerInstanceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlServerInstanceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerInstanceUpdateProperties(_Model):
        always_on_role: Optional[Union[str, AlwaysOnRole]]
        authentication: Optional[Authentication]
        azure_defender_status: Optional[Union[str, DefenderStatus]]
        azure_defender_status_last_updated: Optional[datetime]
        backup_policy: Optional[BackupPolicy]
        best_practices_assessment: Optional[BestPracticesAssessment]
        client_connection: Optional[ClientConnection]
        collation: Optional[str]
        container_resource_id: Optional[str]
        cores: Optional[str]
        create_time: Optional[str]
        current_version: Optional[str]
        database_mirroring_endpoint: Optional[DBMEndpoint]
        db_master_key_exists: Optional[bool]
        discovery_source: Optional[Union[str, DiscoverySource]]
        edition: Optional[Union[str, EditionType]]
        failover_cluster: Optional[FailoverCluster]
        host_type: Optional[Union[str, HostType]]
        instance_name: Optional[str]
        is_digi_cert_pki_cert_trust_configured: Optional[bool]
        is_hadr_enabled: Optional[bool]
        is_microsoft_pki_cert_trust_configured: Optional[bool]
        last_inventory_upload_time: Optional[datetime]
        last_usage_upload_time: Optional[datetime]
        license_type: Optional[Union[str, ArcSqlServerLicenseType]]
        max_server_memory_mb: Optional[int]
        migration: Optional[Migration]
        monitoring: Optional[Monitoring]
        patch_level: Optional[str]
        product_id: Optional[str]
        provisioning_state: Optional[str]
        service_type: Optional[Union[str, ServiceType]]
        status: Optional[Union[str, ConnectionStatus]]
        tcp_dynamic_ports: Optional[str]
        tcp_static_ports: Optional[str]
        trace_flags: Optional[list[int]]
        upgrade_locked_until: Optional[datetime]
        v_core: Optional[str]
        version: Optional[Union[str, SqlVersion]]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[Authentication] = ..., 
                backup_policy: Optional[BackupPolicy] = ..., 
                best_practices_assessment: Optional[BestPracticesAssessment] = ..., 
                client_connection: Optional[ClientConnection] = ..., 
                cores: Optional[str] = ..., 
                database_mirroring_endpoint: Optional[DBMEndpoint] = ..., 
                discovery_source: Optional[Union[str, DiscoverySource]] = ..., 
                edition: Optional[Union[str, EditionType]] = ..., 
                failover_cluster: Optional[FailoverCluster] = ..., 
                host_type: Optional[Union[str, HostType]] = ..., 
                instance_name: Optional[str] = ..., 
                is_digi_cert_pki_cert_trust_configured: Optional[bool] = ..., 
                is_microsoft_pki_cert_trust_configured: Optional[bool] = ..., 
                max_server_memory_mb: Optional[int] = ..., 
                migration: Optional[Migration] = ..., 
                monitoring: Optional[Monitoring] = ..., 
                service_type: Optional[Union[str, ServiceType]] = ..., 
                upgrade_locked_until: Optional[datetime] = ..., 
                version: Optional[Union[str, SqlVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerLicense(TrackedResource):
        id: str
        location: str
        name: str
        properties: SqlServerLicenseProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: SqlServerLicenseProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerLicenseProperties(_Model):
        activation_state: Union[str, ActivationState]
        billing_plan: Union[str, BillingPlan]
        last_activated_at: Optional[datetime]
        last_deactivated_at: Optional[datetime]
        license_category: Union[str, LicenseCategory]
        physical_cores: int
        scope_type: Union[str, ScopeType]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activation_state: Union[str, ActivationState], 
                billing_plan: Union[str, BillingPlan], 
                license_category: Union[str, LicenseCategory], 
                physical_cores: int, 
                scope_type: Union[str, ScopeType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerLicenseUpdate(_Model):
        properties: Optional[SqlServerLicenseUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SqlServerLicenseUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlServerLicenseUpdateProperties(_Model):
        activation_state: Optional[Union[str, ActivationState]]
        billing_plan: Optional[Union[str, BillingPlan]]
        last_activated_at: Optional[datetime]
        last_deactivated_at: Optional[datetime]
        license_category: Optional[Union[str, LicenseCategory]]
        physical_cores: Optional[int]
        scope_type: Optional[Union[str, ScopeType]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activation_state: Optional[Union[str, ActivationState]] = ..., 
                billing_plan: Optional[Union[str, BillingPlan]] = ..., 
                license_category: Optional[Union[str, LicenseCategory]] = ..., 
                physical_cores: Optional[int] = ..., 
                scope_type: Optional[Union[str, ScopeType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.SqlVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SQL_SERVER2012 = "SQL Server 2012"
        SQL_SERVER2014 = "SQL Server 2014"
        SQL_SERVER2016 = "SQL Server 2016"
        SQL_SERVER2017 = "SQL Server 2017"
        SQL_SERVER2019 = "SQL Server 2019"
        SQL_SERVER2022 = "SQL Server 2022"
        SQL_SERVER2025 = "SQL Server 2025"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurearcdata.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        COMPLETED = "Completed"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        FAULTED = "Faulted"
        INACTIVE = "Inactive"
        SUSPENDED = "Suspended"
        TERMINATED = "Terminated"


    class azure.mgmt.azurearcdata.models.SystemData(_Model):
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


    class azure.mgmt.azurearcdata.models.TargetReadiness(_Model):
        azure_sql_database: Optional[SkuRecommendationSummary]
        azure_sql_managed_instance: Optional[SkuRecommendationSummary]
        azure_sql_virtual_machine: Optional[SkuRecommendationSummary]

        @overload
        def __init__(
                self, 
                *, 
                azure_sql_database: Optional[SkuRecommendationSummary] = ..., 
                azure_sql_managed_instance: Optional[SkuRecommendationSummary] = ..., 
                azure_sql_virtual_machine: Optional[SkuRecommendationSummary] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.TargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SQL_DATABASE = "AzureSqlDatabase"
        AZURE_SQL_MANAGED_INSTANCE = "AzureSqlManagedInstance"
        AZURE_SQL_VIRTUAL_MACHINE = "AzureSqlVirtualMachine"


    class azure.mgmt.azurearcdata.models.TrackedResource(Resource):
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


    class azure.mgmt.azurearcdata.models.UploadServicePrincipal(_Model):
        authority: Optional[str]
        client_id: Optional[str]
        client_secret: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authority: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.UploadWatermark(_Model):
        logs: Optional[datetime]
        metrics: Optional[datetime]
        usages: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[datetime] = ..., 
                metrics: Optional[datetime] = ..., 
                usages: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurearcdata.models.Version(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SQL_SERVER2012 = "SQL Server 2012"
        SQL_SERVER2014 = "SQL Server 2014"
        SQL_SERVER2016 = "SQL Server 2016"


namespace azure.mgmt.azurearcdata.operations

    class azure.mgmt.azurearcdata.operations.ActiveDirectoryConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: ActiveDirectoryConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ActiveDirectoryConnectorResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: ActiveDirectoryConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ActiveDirectoryConnectorResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                active_directory_connector_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ActiveDirectoryConnectorResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                active_directory_connector_name: str, 
                **kwargs: Any
            ) -> ActiveDirectoryConnectorResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ActiveDirectoryConnectorResource]: ...


    class azure.mgmt.azurearcdata.operations.DataControllersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_patch_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: DataControllerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @overload
        def begin_put_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                data_controller_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataControllerResource]: ...

        @distributed_trace
        def get_data_controller(
                self, 
                resource_group_name: str, 
                data_controller_name: str, 
                **kwargs: Any
            ) -> DataControllerResource: ...

        @distributed_trace
        def list_in_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataControllerResource]: ...

        @distributed_trace
        def list_in_subscription(self, **kwargs: Any) -> ItemPaged[DataControllerResource]: ...


    class azure.mgmt.azurearcdata.operations.FailoverGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                failover_group_resource: FailoverGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailoverGroupResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                failover_group_resource: FailoverGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailoverGroupResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                failover_group_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailoverGroupResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                failover_group_name: str, 
                **kwargs: Any
            ) -> FailoverGroupResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FailoverGroupResource]: ...


    class azure.mgmt.azurearcdata.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.azurearcdata.operations.PostgresInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: PostgresInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostgresInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: PostgresInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostgresInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostgresInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[PostgresInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PostgresInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: PostgresInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: PostgresInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                postgres_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PostgresInstance: ...


    class azure.mgmt.azurearcdata.operations.SqlManagedInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: SqlManagedInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlManagedInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: SqlManagedInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlManagedInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                sql_managed_instance: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlManagedInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SqlManagedInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlManagedInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: SqlManagedInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: SqlManagedInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_managed_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlManagedInstance: ...


    class azure.mgmt.azurearcdata.operations.SqlServerAvailabilityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        def add_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        def add_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        def begin_create_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_ag_configuration: AvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_ag_configuration: AvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_ag_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_distributed_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_dag_configuration: DistributedAvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_distributed_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_dag_configuration: DistributedAvailabilityGroupCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_distributed_availability_group(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_dag_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_managed_instance_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_managed_instance_link_configuration: ManagedInstanceLinkCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_managed_instance_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_managed_instance_link_configuration: ManagedInstanceLinkCreateUpdateConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_create_managed_instance_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                create_managed_instance_link_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_failover_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                managed_instance_resource_id: FailoverMiLinkResourceId, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_failover_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                managed_instance_resource_id: FailoverMiLinkResourceId, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_failover_mi_link(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                managed_instance_resource_id: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_update: SqlServerAvailabilityGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_update: SqlServerAvailabilityGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerAvailabilityGroupResource]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_resource: SqlServerAvailabilityGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_resource: SqlServerAvailabilityGroupResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                sql_server_availability_group_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace
        def detail_view(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace
        def failover(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace
        def force_failover_allow_data_loss(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        def remove_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        def remove_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: Databases, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...

        @overload
        def remove_databases(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_name: str, 
                databases: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerAvailabilityGroupResource: ...


    class azure.mgmt.azurearcdata.operations.SqlServerDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_update: SqlServerDatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerDatabaseResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_update: SqlServerDatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerDatabaseResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerDatabaseResource]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_resource: SqlServerDatabaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_resource: SqlServerDatabaseResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                sql_server_database_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                database_name: str, 
                **kwargs: Any
            ) -> SqlServerDatabaseResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlServerDatabaseResource]: ...


    class azure.mgmt.azurearcdata.operations.SqlServerEsuLicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                sql_server_esu_license: SqlServerEsuLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                sql_server_esu_license: SqlServerEsuLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                sql_server_esu_license: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SqlServerEsuLicense]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlServerEsuLicense]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                parameters: SqlServerEsuLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                parameters: SqlServerEsuLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_esu_license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerEsuLicense: ...


    class azure.mgmt.azurearcdata.operations.SqlServerInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: SqlServerInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: SqlServerInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_bpa_request: SqlServerInstanceBpaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[List[str]]]: ...

        @overload
        def begin_get_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_bpa_request: SqlServerInstanceBpaRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[List[str]]]: ...

        @overload
        def begin_get_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_bpa_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[List[str]]]: ...

        @overload
        def begin_get_jobs(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_request: Optional[SqlServerInstanceJobsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceJobsResponse]: ...

        @overload
        def begin_get_jobs(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_request: Optional[SqlServerInstanceJobsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceJobsResponse]: ...

        @overload
        def begin_get_jobs(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceJobsResponse]: ...

        @distributed_trace
        def begin_get_migration_readiness_report(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceMigrationReadinessReportResponse]: ...

        @overload
        def begin_get_target_recommendation_reports(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_target_recommendation_reports_request: Optional[SqlServerInstanceTargetRecommendationReportsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceTargetRecommendationReportsResponse]: ...

        @overload
        def begin_get_target_recommendation_reports(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_target_recommendation_reports_request: Optional[SqlServerInstanceTargetRecommendationReportsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceTargetRecommendationReportsResponse]: ...

        @overload
        def begin_get_target_recommendation_reports(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_target_recommendation_reports_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceTargetRecommendationReportsResponse]: ...

        @overload
        def begin_get_telemetry(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_telemetry_request: SqlServerInstanceTelemetryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[List[str]]]: ...

        @overload
        def begin_get_telemetry(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_telemetry_request: SqlServerInstanceTelemetryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[List[str]]]: ...

        @overload
        def begin_get_telemetry(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_telemetry_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[List[str]]]: ...

        @distributed_trace
        def begin_run_best_practice_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceRunBestPracticesAssessmentResponse]: ...

        @overload
        def begin_run_managed_instance_link_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_managed_instance_link_assessment_request: SqlServerInstanceManagedInstanceLinkAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceManagedInstanceLinkAssessmentResponse]: ...

        @overload
        def begin_run_managed_instance_link_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_managed_instance_link_assessment_request: SqlServerInstanceManagedInstanceLinkAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceManagedInstanceLinkAssessmentResponse]: ...

        @overload
        def begin_run_managed_instance_link_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_managed_instance_link_assessment_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceManagedInstanceLinkAssessmentResponse]: ...

        @distributed_trace
        def begin_run_migration_readiness_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceRunMigrationReadinessAssessmentResponse]: ...

        @overload
        def begin_run_target_recommendation_job(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_run_target_recommendation_job_request: Optional[SqlServerInstanceRunTargetRecommendationJobRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceRunTargetRecommendationJobResponse]: ...

        @overload
        def begin_run_target_recommendation_job(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_run_target_recommendation_job_request: Optional[SqlServerInstanceRunTargetRecommendationJobRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceRunTargetRecommendationJobResponse]: ...

        @overload
        def begin_run_target_recommendation_job(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_run_target_recommendation_job_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstanceRunTargetRecommendationJobResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: SqlServerInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: SqlServerInstanceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlServerInstance]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @overload
        def get_all_availability_groups(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_retrieval_filters: Optional[AvailabilityGroupRetrievalFilters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        def get_all_availability_groups(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_retrieval_filters: Optional[AvailabilityGroupRetrievalFilters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        def get_all_availability_groups(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                availability_group_retrieval_filters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[SqlServerAvailabilityGroupResource]: ...

        @overload
        def get_jobs_status(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_status_request: Optional[SqlServerInstanceJobsStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstanceJobsStatusResponse: ...

        @overload
        def get_jobs_status(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_status_request: Optional[SqlServerInstanceJobsStatusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstanceJobsStatusResponse: ...

        @overload
        def get_jobs_status(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                sql_server_instance_jobs_status_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerInstanceJobsStatusResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SqlServerInstance]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlServerInstance]: ...

        @distributed_trace
        def post_upgrade(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @distributed_trace
        def pre_upgrade(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstance: ...

        @distributed_trace
        def run_best_practices_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstanceRunBestPracticesAssessmentResponse: ...

        @distributed_trace
        def run_migration_assessment(
                self, 
                resource_group_name: str, 
                sql_server_instance_name: str, 
                **kwargs: Any
            ) -> SqlServerInstanceRunMigrationAssessmentResponse: ...


    class azure.mgmt.azurearcdata.operations.SqlServerLicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                sql_server_license: SqlServerLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                sql_server_license: SqlServerLicense, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                sql_server_license: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SqlServerLicense]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlServerLicense]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                parameters: SqlServerLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                parameters: SqlServerLicenseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sql_server_license_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SqlServerLicense: ...


namespace azure.mgmt.azurearcdata.types

    class azure.mgmt.azurearcdata.types.ActiveDirectoryConnectorDNSDetails(TypedDict, total=False):
        key "domainName": str
        key "nameserverIPAddresses": Required[list[str]]
        key "preferK8sDnsForPtrLookups": bool
        key "replicas": int
        domain_name: str
        nameserver_ip_addresses: list[str]
        prefer_k8_s_dns_for_ptr_lookups: bool
        replicas: int


    class azure.mgmt.azurearcdata.types.ActiveDirectoryConnectorDomainDetails(TypedDict, total=False):
        key "domainControllers": ForwardRef('ActiveDirectoryDomainControllers', module='types')
        key "netbiosDomainName": str
        key "ouDistinguishedName": str
        key "realm": Required[str]
        key "serviceAccountProvisioning": Union[str, AccountProvisioningMode]
        domain_controllers: ActiveDirectoryDomainControllers
        netbios_domain_name: str
        ou_distinguished_name: str
        realm: str
        service_account_provisioning: Union[str, AccountProvisioningMode]


    class azure.mgmt.azurearcdata.types.ActiveDirectoryConnectorProperties(TypedDict, total=False):
        key "domainServiceAccountLoginInformation": ForwardRef('BasicLoginInformation', module='types')
        key "provisioningState": str
        key "spec": Required[ActiveDirectoryConnectorSpec]
        key "status": ForwardRef('ActiveDirectoryConnectorStatus', module='types')
        domain_service_account_login_information: BasicLoginInformation
        provisioning_state: str
        spec: ActiveDirectoryConnectorSpec
        status: ActiveDirectoryConnectorStatus


    class azure.mgmt.azurearcdata.types.ActiveDirectoryConnectorResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ActiveDirectoryConnectorProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ActiveDirectoryConnectorProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurearcdata.types.ActiveDirectoryConnectorSpec(TypedDict, total=False):
        key "activeDirectory": Required[ActiveDirectoryConnectorDomainDetails]
        key "dns": Required[ActiveDirectoryConnectorDNSDetails]
        active_directory: ActiveDirectoryConnectorDomainDetails
        dns: ActiveDirectoryConnectorDNSDetails


    class azure.mgmt.azurearcdata.types.ActiveDirectoryConnectorStatus(TypedDict, total=False):
        key "lastUpdateTime": str
        key "observedGeneration": int
        key "state": str
        last_update_time: str
        observed_generation: int
        state: str


    class azure.mgmt.azurearcdata.types.ActiveDirectoryDomainController(TypedDict, total=False):
        key "hostname": Required[str]
        hostname: str


    class azure.mgmt.azurearcdata.types.ActiveDirectoryDomainControllers(TypedDict, total=False):
        key "primaryDomainController": ForwardRef('ActiveDirectoryDomainController', module='types')
        primary_domain_controller: ActiveDirectoryDomainController
        secondaryDomainControllers: list[ActiveDirectoryDomainController]
        secondary_domain_controllers: list[ActiveDirectoryDomainController]


    class azure.mgmt.azurearcdata.types.ActiveDirectoryInformation(TypedDict, total=False):
        key "keytabInformation": ForwardRef('KeytabInformation', module='types')
        keytab_information: KeytabInformation


    class azure.mgmt.azurearcdata.types.AdditionalMigrationJobAttributes(TypedDict, total=False):
        key "keyName": str
        key "keyValue": str
        key_name: str
        key_value: str


    class azure.mgmt.azurearcdata.types.Authentication(TypedDict, total=False):
        key "mode": Union[str, Mode]
        mode: Union[str, Mode]
        sqlServerEntraIdentity: list[EntraAuthentication]
        sql_server_entra_identity: list[EntraAuthentication]


    class azure.mgmt.azurearcdata.types.AvailabilityGroupConfigure(TypedDict, total=False):
        key "availabilityMode": Union[str, ArcSqlServerAvailabilityMode]
        key "availabilityModeDescription": str
        key "backupPriority": int
        key "certificateName": str
        key "endpointAuthenticationMode": Union[str, ConnectionAuth]
        key "endpointConnectLogin": str
        key "endpointName": str
        key "endpointUrl": str
        key "failoverMode": Union[str, ArcSqlServerFailoverMode]
        key "failoverModeDescription": str
        key "primaryAllowConnections": Union[str, PrimaryAllowConnections]
        key "primaryRoleAllowConnectionsDescription": str
        key "readOnlyRoutingUrl": str
        key "readWriteRoutingUrl": str
        key "replicaCreateDate": str
        key "replicaModifyDate": str
        key "secondaryAllowConnections": Union[str, SecondaryAllowConnections]
        key "secondaryRoleAllowConnectionsDescription": str
        key "seedingMode": Union[str, SeedingMode]
        key "seedingModeDescription": str
        key "sessionTimeout": int
        availability_mode: Union[str, ArcSqlServerAvailabilityMode]
        availability_mode_description: str
        backup_priority: int
        certificate_name: str
        endpoint_authentication_mode: Union[str, ConnectionAuth]
        endpoint_connect_login: str
        endpoint_name: str
        endpoint_url: str
        failover_mode: Union[str, ArcSqlServerFailoverMode]
        failover_mode_description: str
        primary_allow_connections: Union[str, PrimaryAllowConnections]
        primary_role_allow_connections_description: str
        read_only_routing_url: str
        read_write_routing_url: str
        replica_create_date: str
        replica_modify_date: str
        secondary_allow_connections: Union[str, SecondaryAllowConnections]
        secondary_role_allow_connections_description: str
        seeding_mode: Union[str, SeedingMode]
        seeding_mode_description: str
        session_timeout: int


    class azure.mgmt.azurearcdata.types.AvailabilityGroupCreateUpdateConfiguration(TypedDict, total=False):
        key "automatedBackupPreference": Union[str, AutomatedBackupPreference]
        key "availabilityGroupName": str
        key "clusterType": Union[str, ClusterType]
        key "dbFailover": Union[str, DbFailover]
        key "dtcSupport": Union[str, DtcSupport]
        key "failureConditionLevel": Union[int, FailureConditionLevel]
        key "healthCheckTimeout": int
        key "listener": ForwardRef('SqlAvailabilityGroupStaticIPListenerProperties', module='types')
        key "requiredSynchronizedSecondariesToCommit": int
        automated_backup_preference: Union[str, AutomatedBackupPreference]
        availability_group_name: str
        cluster_type: Union[str, ClusterType]
        databases: list[str]
        db_failover: Union[str, DbFailover]
        dtc_support: Union[str, DtcSupport]
        failure_condition_level: Union[int, FailureConditionLevel]
        health_check_timeout: int
        listener: SqlAvailabilityGroupStaticIPListenerProperties
        replicas: list[AvailabilityGroupCreateUpdateReplicaConfiguration]
        required_synchronized_secondaries_to_commit: int


    class azure.mgmt.azurearcdata.types.AvailabilityGroupCreateUpdateReplicaConfiguration(TypedDict, total=False):
        key "availabilityMode": Union[str, ArcSqlServerAvailabilityMode]
        key "backupPriority": int
        key "certificateName": str
        key "endpointAuthenticationMode": Union[str, ConnectionAuth]
        key "endpointConnectLogin": str
        key "endpointName": str
        key "endpointUrl": str
        key "failoverMode": Union[str, ArcSqlServerFailoverMode]
        key "primaryRoleAllowConnections": Union[str, PrimaryAllowConnections]
        key "secondaryRoleAllowConnections": Union[str, SecondaryAllowConnections]
        key "secondaryRoleReadOnlyRoutingUrl": str
        key "seedingMode": Union[str, SeedingMode]
        key "serverInstance": str
        key "sessionTimeout": int
        availability_mode: Union[str, ArcSqlServerAvailabilityMode]
        backup_priority: int
        certificate_name: str
        endpoint_authentication_mode: Union[str, ConnectionAuth]
        endpoint_connect_login: str
        endpoint_name: str
        endpoint_url: str
        failover_mode: Union[str, ArcSqlServerFailoverMode]
        primaryRoleReadOnlyRoutingList: list[str]
        primary_role_allow_connections: Union[str, PrimaryAllowConnections]
        primary_role_read_only_routing_list: list[str]
        secondary_role_allow_connections: Union[str, SecondaryAllowConnections]
        secondary_role_read_only_routing_url: str
        seeding_mode: Union[str, SeedingMode]
        server_instance: str
        session_timeout: int


    class azure.mgmt.azurearcdata.types.AvailabilityGroupInfo(TypedDict, total=False):
        key "automatedBackupPreferenceDescription": str
        key "basicFeatures": bool
        key "clusterTypeDescription": str
        key "dbFailover": bool
        key "dtcSupport": bool
        key "failureConditionLevel": int
        key "healthCheckTimeout": int
        key "isContained": bool
        key "isDistributed": bool
        key "listener": ForwardRef('SqlAvailabilityGroupStaticIPListenerProperties', module='types')
        key "primaryRecoveryHealthDescription": str
        key "primaryReplica": str
        key "replicationPartnerType": Union[str, ReplicationPartnerType]
        key "requiredSynchronizedSecondariesToCommit": int
        key "secondaryRecoveryHealthDescription": str
        key "synchronizationHealthDescription": str
        key "version": int
        automated_backup_preference_description: str
        basic_features: bool
        cluster_type_description: str
        db_failover: bool
        dtc_support: bool
        failure_condition_level: int
        health_check_timeout: int
        is_contained: bool
        is_distributed: bool
        listener: SqlAvailabilityGroupStaticIPListenerProperties
        primary_recovery_health_description: str
        primary_replica: str
        replication_partner_type: Union[str, ReplicationPartnerType]
        required_synchronized_secondaries_to_commit: int
        secondary_recovery_health_description: str
        synchronization_health_description: str
        version: int


    class azure.mgmt.azurearcdata.types.AvailabilityGroupRetrievalFilters(TypedDict, total=False):
        key "availabilityGroupTypeFilter": Union[str, ArcSqlServerAvailabilityGroupTypeFilter]
        key "replicationPartnerTypeFilter": Union[str, ReplicationPartnerType]
        availability_group_type_filter: Union[str, ArcSqlServerAvailabilityGroupTypeFilter]
        replication_partner_type_filter: Union[str, ReplicationPartnerType]


    class azure.mgmt.azurearcdata.types.AvailabilityGroupState(TypedDict, total=False):
        key "availabilityGroupReplicaRole": str
        key "connectedStateDescription": str
        key "lastConnectErrorDescription": str
        key "lastConnectErrorTimestamp": str
        key "operationalStateDescription": str
        key "recoveryHealthDescription": str
        key "synchronizationHealthDescription": str
        availability_group_replica_role: str
        connected_state_description: str
        last_connect_error_description: str
        last_connect_error_timestamp: str
        operational_state_description: str
        recovery_health_description: str
        synchronization_health_description: str


    class azure.mgmt.azurearcdata.types.BackgroundJob(TypedDict, total=False):
        key "endTime": str
        key "executionState": Union[str, ExecutionState]
        key "lastExecutionStatus": Union[str, LastExecutionStatus]
        key "lastExecutionTime": str
        key "nextExecutionTime": str
        key "startTime": str
        key "state": Union[str, State]
        end_time: str
        execution_state: Union[str, ExecutionState]
        last_execution_status: Union[str, LastExecutionStatus]
        last_execution_time: str
        next_execution_time: str
        start_time: str
        state: Union[str, State]


    class azure.mgmt.azurearcdata.types.BackupPolicy(TypedDict, total=False):
        key "differentialBackupHours": Union[int, DifferentialBackupHours]
        key "fullBackupDays": int
        key "retentionPeriodDays": int
        key "transactionLogBackupMinutes": int
        differential_backup_hours: Union[int, DifferentialBackupHours]
        full_backup_days: int
        retention_period_days: int
        transaction_log_backup_minutes: int


    class azure.mgmt.azurearcdata.types.BasicLoginInformation(TypedDict, total=False):
        key "password": str
        key "username": str
        password: str
        username: str


    class azure.mgmt.azurearcdata.types.BestPracticesAssessment(TypedDict, total=False):
        key "enabled": bool
        key "schedule": ForwardRef('Schedule', module='types')
        enabled: bool
        schedule: Schedule


    class azure.mgmt.azurearcdata.types.ClientConnection(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.azurearcdata.types.CommonSku(TypedDict, total=False):
        key "capacity": int
        key "dev": bool
        key "family": str
        key "name": Required[str]
        key "size": str
        capacity: int
        dev: bool
        family: str
        name: str
        size: str


    class azure.mgmt.azurearcdata.types.CostOptionSelectedValues(TypedDict, total=False):
        key "computeAndStorageCostOption": str
        key "sqlLicenseCostOption": str
        key "windowsLicenseCostOption": str
        compute_and_storage_cost_option: str
        sql_license_cost_option: str
        windows_license_cost_option: str


    class azure.mgmt.azurearcdata.types.CostTypeValues(TypedDict, total=False):
        key "computeCost": float
        key "iopsCost": float
        key "storageCost": float
        compute_cost: float
        iops_cost: float
        storage_cost: float


    class azure.mgmt.azurearcdata.types.CronTrigger(TypedDict, total=False):
        key "expression": str
        key "startTime": str
        key "timeZone": str
        expression: str
        start_time: str
        time_zone: str


    class azure.mgmt.azurearcdata.types.DBMEndpoint(TypedDict, total=False):
        key "certificateExpiryDate": str
        key "certificateName": str
        key "connectionAuth": Union[str, ConnectionAuth]
        key "encryptionAlgorithm": Union[str, EncryptionAlgorithm]
        key "endpointName": str
        key "ipAddress": str
        key "isDynamicPort": bool
        key "isEncryptionEnabled": bool
        key "port": int
        key "role": Union[str, Role]
        certificate_expiry_date: str
        certificate_name: str
        connection_auth: Union[str, ConnectionAuth]
        encryption_algorithm: Union[str, EncryptionAlgorithm]
        endpoint_name: str
        ip_address: str
        is_dynamic_port: bool
        is_encryption_enabled: bool
        port: int
        role: Union[str, Role]


    class azure.mgmt.azurearcdata.types.DataBaseMigration(TypedDict, total=False):
        key "assessment": ForwardRef('DataBaseMigrationAssessment', module='types')
        assessment: DataBaseMigrationAssessment
        jobs: list[DatabaseMigrationJobsItem]


    class azure.mgmt.azurearcdata.types.DataBaseMigrationAssessment(TypedDict, total=False):
        key "assessmentUploadTime": str
        key "targetReadiness": ForwardRef('TargetReadiness', module='types')
        key "targetRecommendationGenerationTime": str
        assessment_upload_time: str
        databaseAssessments: list[DatabaseAssessmentsItem]
        database_assessments: list[DatabaseAssessmentsItem]
        target_readiness: TargetReadiness
        target_recommendation_generation_time: str


    class azure.mgmt.azurearcdata.types.DataControllerProperties(TypedDict, total=False):
        key "basicLoginInformation": ForwardRef('BasicLoginInformation', module='types')
        key "clusterId": str
        key "extensionId": str
        key "infrastructure": Union[str, Infrastructure]
        key "k8sRaw": Any
        key "lastUploadedDate": str
        key "logAnalyticsWorkspaceConfig": ForwardRef('LogAnalyticsWorkspaceConfig', module='types')
        key "logsDashboardCredential": ForwardRef('BasicLoginInformation', module='types')
        key "metricsDashboardCredential": ForwardRef('BasicLoginInformation', module='types')
        key "onPremiseProperty": ForwardRef('OnPremiseProperty', module='types')
        key "provisioningState": str
        key "uploadServicePrincipal": ForwardRef('UploadServicePrincipal', module='types')
        key "uploadWatermark": ForwardRef('UploadWatermark', module='types')
        basic_login_information: BasicLoginInformation
        cluster_id: str
        extension_id: str
        infrastructure: Union[str, Infrastructure]
        k8_s_raw: Any
        last_uploaded_date: str
        log_analytics_workspace_config: LogAnalyticsWorkspaceConfig
        logs_dashboard_credential: BasicLoginInformation
        metrics_dashboard_credential: BasicLoginInformation
        on_premise_property: OnPremiseProperty
        provisioning_state: str
        upload_service_principal: UploadServicePrincipal
        upload_watermark: UploadWatermark


    class azure.mgmt.azurearcdata.types.DataControllerResource(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[DataControllerProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: DataControllerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.DataControllerUpdate(TypedDict, total=False):
        key "properties": ForwardRef('DataControllerProperties', module='types')
        properties: DataControllerProperties
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.DatabaseAssessmentsItem(TypedDict, total=False):
        key "appliesToMigrationTargetPlatform": str
        key "featureId": str
        key "issueCategory": str
        key "moreInformation": str
        applies_to_migration_target_platform: str
        feature_id: str
        issue_category: str
        more_information: str


    class azure.mgmt.azurearcdata.types.DatabaseMigrationJobsItem(TypedDict, total=False):
        key "endTime": str
        key "initiatedFrom": Union[str, InitiatedFrom]
        key "lastError": str
        key "migrationMode": Union[str, MigrationMode]
        key "migrationTrackingId": str
        key "startTime": str
        key "status": Union[str, MigrationStatus]
        key "targetResourceId": str
        key "targetType": Union[str, TargetType]
        additionalAttributes: list[AdditionalMigrationJobAttributes]
        additional_attributes: list[AdditionalMigrationJobAttributes]
        end_time: str
        initiated_from: Union[str, InitiatedFrom]
        last_error: str
        migration_mode: Union[str, MigrationMode]
        migration_tracking_id: str
        start_time: str
        status: Union[str, MigrationStatus]
        target_resource_id: str
        target_type: Union[str, TargetType]


    class azure.mgmt.azurearcdata.types.Databases(TypedDict, total=False):
        values: list[str]
        values_property: list[str]


    class azure.mgmt.azurearcdata.types.DiskSizes(TypedDict, total=False):
        key "caching": str
        key "diskType": str
        key "maxIops": float
        key "maxSizeInGib": float
        key "maxThroughputInMbps": float
        key "redundancy": str
        key "size": str
        caching: str
        disk_type: str
        max_iops: float
        max_size_in_gib: float
        max_throughput_in_mbps: float
        redundancy: str
        size: str


    class azure.mgmt.azurearcdata.types.DistributedAvailabilityGroupCreateUpdateAvailabilityGroupCertificateConfiguration(TypedDict, total=False):
        key "certificateName": str
        certificate_name: str


    class azure.mgmt.azurearcdata.types.DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration(TypedDict, total=False):
        key "availabilityGroup": str
        key "availabilityMode": Union[str, ArcSqlServerAvailabilityMode]
        key "certificateConfiguration": ForwardRef('DistributedAvailabilityGroupCreateUpdateAvailabilityGroupCertificateConfiguration', module='types')
        key "failoverMode": Union[str, ArcSqlServerFailoverMode]
        key "listenerUrl": str
        key "seedingMode": Union[str, SeedingMode]
        availability_group: str
        availability_mode: Union[str, ArcSqlServerAvailabilityMode]
        certificate_configuration: DistributedAvailabilityGroupCreateUpdateAvailabilityGroupCertificateConfiguration
        failover_mode: Union[str, ArcSqlServerFailoverMode]
        listener_url: str
        seeding_mode: Union[str, SeedingMode]


    class azure.mgmt.azurearcdata.types.DistributedAvailabilityGroupCreateUpdateConfiguration(TypedDict, total=False):
        key "availabilityGroupName": str
        key "primaryAvailabilityGroup": ForwardRef('DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration', module='types')
        key "secondaryAvailabilityGroup": ForwardRef('DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration', module='types')
        availability_group_name: str
        primary_availability_group: DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration
        secondary_availability_group: DistributedAvailabilityGroupCreateUpdateAvailabilityGroupConfiguration


    class azure.mgmt.azurearcdata.types.EntraAuthentication(TypedDict, total=False):
        key "clientId": str
        key "identityType": Union[str, IdentityType]
        client_id: str
        identity_type: Union[str, IdentityType]


    class azure.mgmt.azurearcdata.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.azurearcdata.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.azurearcdata.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.azurearcdata.types.ExtendedLocation(TypedDict, total=False):
        key "name": str
        key "type": Union[str, ExtendedLocationTypes]
        name: str
        type: Union[str, ExtendedLocationTypes]


    class azure.mgmt.azurearcdata.types.FailoverCluster(TypedDict, total=False):
        key "id": str
        key "networkName": str
        hostIPAddresses: list[HostIPAddressInformation]
        hostNames: list[str]
        host_ip_addresses: list[HostIPAddressInformation]
        host_names: list[str]
        id: str
        network_name: str
        sqlInstanceIds: list[str]
        sql_instance_ids: list[str]


    class azure.mgmt.azurearcdata.types.FailoverGroupProperties(TypedDict, total=False):
        key "partnerManagedInstanceId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "spec": Required[FailoverGroupSpec]
        key "status": Any
        partner_managed_instance_id: str
        provisioning_state: Union[str, ProvisioningState]
        spec: FailoverGroupSpec
        status: Any


    class azure.mgmt.azurearcdata.types.FailoverGroupResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[FailoverGroupProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FailoverGroupProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurearcdata.types.FailoverGroupSpec(TypedDict, total=False):
        key "partnerMI": str
        key "partnerMirroringCert": str
        key "partnerMirroringURL": str
        key "partnerSyncMode": Union[str, FailoverGroupPartnerSyncMode]
        key "role": Required[Union[str, InstanceFailoverGroupRole]]
        key "sharedName": str
        key "sourceMI": str
        partner_mi: str
        partner_mirroring_cert: str
        partner_mirroring_url: str
        partner_sync_mode: Union[str, FailoverGroupPartnerSyncMode]
        role: Union[str, InstanceFailoverGroupRole]
        shared_name: str
        source_mi: str


    class azure.mgmt.azurearcdata.types.FailoverMiLinkResourceId(TypedDict, total=False):
        key "force": bool
        key "managedInstanceId": str
        force: bool
        managed_instance_id: str


    class azure.mgmt.azurearcdata.types.HostIPAddressInformation(TypedDict, total=False):
        key "ipAddress": str
        key "subnetMask": str
        ip_address: str
        subnet_mask: str


    class azure.mgmt.azurearcdata.types.ImpactedObjectsInfo(TypedDict, total=False):
        key "featureId": str
        key "issueCategory": str
        key "numberImpacted": int
        feature_id: str
        issue_category: str
        number_impacted: int


    class azure.mgmt.azurearcdata.types.ImpactedObjectsSuitabilitySummary(TypedDict, total=False):
        azureSqlDatabase: list[ImpactedObjectsInfo]
        azureSqlManagedInstance: list[ImpactedObjectsInfo]
        azure_sql_database: list[ImpactedObjectsInfo]
        azure_sql_managed_instance: list[ImpactedObjectsInfo]


    class azure.mgmt.azurearcdata.types.K8SActiveDirectory(TypedDict, total=False):
        key "accountName": str
        key "connector": ForwardRef('K8SActiveDirectoryConnector', module='types')
        key "keytabSecret": str
        account_name: str
        connector: K8SActiveDirectoryConnector
        encryptionTypes: list[str]
        encryption_types: list[str]
        keytab_secret: str


    class azure.mgmt.azurearcdata.types.K8SActiveDirectoryConnector(TypedDict, total=False):
        key "name": str
        key "namespace": str
        name: str
        namespace: str


    class azure.mgmt.azurearcdata.types.K8SNetworkSettings(TypedDict, total=False):
        key "forceencryption": int
        key "tlsciphers": str
        key "tlsprotocols": str
        forceencryption: int
        tlsciphers: str
        tlsprotocols: str


    class azure.mgmt.azurearcdata.types.K8SResourceRequirements(TypedDict, total=False):
        limits: dict[str, str]
        requests: dict[str, str]


    class azure.mgmt.azurearcdata.types.K8SScheduling(TypedDict, total=False):
        key "default": ForwardRef('K8SSchedulingOptions', module='types')
        default: K8SSchedulingOptions


    class azure.mgmt.azurearcdata.types.K8SSchedulingOptions(TypedDict, total=False):
        key "resources": ForwardRef('K8SResourceRequirements', module='types')
        resources: K8SResourceRequirements


    class azure.mgmt.azurearcdata.types.K8SSecurity(TypedDict, total=False):
        key "activeDirectory": ForwardRef('K8SActiveDirectory', module='types')
        key "adminLoginSecret": str
        key "serviceCertificateSecret": str
        key "transparentDataEncryption": ForwardRef('K8StransparentDataEncryption', module='types')
        active_directory: K8SActiveDirectory
        admin_login_secret: str
        service_certificate_secret: str
        transparent_data_encryption: K8StransparentDataEncryption


    class azure.mgmt.azurearcdata.types.K8SSettings(TypedDict, total=False):
        key "network": ForwardRef('K8SNetworkSettings', module='types')
        network: K8SNetworkSettings


    class azure.mgmt.azurearcdata.types.K8StransparentDataEncryption(TypedDict, total=False):
        key "mode": str
        key "protectorSecret": str
        mode: str
        protector_secret: str


    class azure.mgmt.azurearcdata.types.KeytabInformation(TypedDict, total=False):
        key "keytab": str
        keytab: str


    class azure.mgmt.azurearcdata.types.LogAnalyticsWorkspaceConfig(TypedDict, total=False):
        key "primaryKey": str
        key "workspaceId": str
        primary_key: str
        workspace_id: str


    class azure.mgmt.azurearcdata.types.ManagedInstanceLinkCreateUpdateConfiguration(TypedDict, total=False):
        key "availabilityGroup": ForwardRef('AvailabilityGroupCreateUpdateConfiguration', module='types')
        key "distributedAvailabilityGroup": ForwardRef('DistributedAvailabilityGroupCreateUpdateConfiguration', module='types')
        key "miLinkConfiguration": ForwardRef('MiLinkCreateUpdateConfiguration', module='types')
        availability_group: AvailabilityGroupCreateUpdateConfiguration
        distributed_availability_group: DistributedAvailabilityGroupCreateUpdateConfiguration
        mi_link_configuration: MiLinkCreateUpdateConfiguration


    class azure.mgmt.azurearcdata.types.MiLinkCreateUpdateConfiguration(TypedDict, total=False):
        key "instanceAvailabilityGroupName": str
        instance_availability_group_name: str


    class azure.mgmt.azurearcdata.types.Migration(TypedDict, total=False):
        key "assessment": ForwardRef('MigrationAssessment', module='types')
        key "targetResourceId": str
        key "targetSelectedTime": str
        assessment: MigrationAssessment
        target_resource_id: str
        target_selected_time: str


    class azure.mgmt.azurearcdata.types.MigrationAssessment(TypedDict, total=False):
        key "assessmentUploadTime": str
        key "assessmentViewedTime": str
        key "enabled": bool
        key "impactedObjectsSummary": ForwardRef('ImpactedObjectsSuitabilitySummary', module='types')
        key "settings": ForwardRef('MigrationAssessmentSettings', module='types')
        key "skuRecommendationResults": ForwardRef('SkuRecommendationResults', module='types')
        key "targetRecommendationGenerationTime": str
        key "version": str
        assessment_upload_time: str
        assessment_viewed_time: str
        enabled: bool
        impacted_objects_summary: ImpactedObjectsSuitabilitySummary
        serverAssessments: list[ServerAssessmentsItem]
        server_assessments: list[ServerAssessmentsItem]
        settings: MigrationAssessmentSettings
        sku_recommendation_results: SkuRecommendationResults
        target_recommendation_generation_time: str
        version: str


    class azure.mgmt.azurearcdata.types.MigrationAssessmentSettings(TypedDict, total=False):
        key "comfortFactor": int
        key "costOptions": ForwardRef('CostOptionSelectedValues', module='types')
        key "currency": str
        key "discountPercentage": float
        key "lookbackPeriodInDays": int
        key "percentile": float
        key "strategy": str
        key "targetLocation": str
        comfort_factor: int
        cost_options: CostOptionSelectedValues
        currency: str
        discount_percentage: float
        lookback_period_in_days: int
        percentile: float
        strategy: str
        target_location: str


    class azure.mgmt.azurearcdata.types.Monitoring(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.azurearcdata.types.OnPremiseProperty(TypedDict, total=False):
        key "id": Required[str]
        key "publicSigningKey": Required[str]
        key "signingCertificateThumbprint": str
        id: str
        public_signing_key: str
        signing_certificate_thumbprint: str


    class azure.mgmt.azurearcdata.types.Operation(TypedDict, total=False):
        key "display": Required[OperationDisplay]
        key "isDataAction": Required[bool]
        key "name": Required[str]
        key "origin": Union[str, OperationOrigin]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, OperationOrigin]
        properties: dict[str, Any]


    class azure.mgmt.azurearcdata.types.OperationDisplay(TypedDict, total=False):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.azurearcdata.types.PostgresInstance(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[PostgresInstanceProperties]
        key "sku": ForwardRef('PostgresInstanceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: PostgresInstanceProperties
        sku: PostgresInstanceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.PostgresInstanceProperties(TypedDict, total=False):
        key "admin": str
        key "basicLoginInformation": ForwardRef('BasicLoginInformation', module='types')
        key "dataControllerId": str
        key "k8sRaw": Any
        key "lastUploadedDate": str
        key "provisioningState": str
        admin: str
        basic_login_information: BasicLoginInformation
        data_controller_id: str
        k8_s_raw: Any
        last_uploaded_date: str
        provisioning_state: str


    class azure.mgmt.azurearcdata.types.PostgresInstanceSku(CommonSku):
        key "capacity": int
        key "dev": bool
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Literal["Hyperscale"]
        capacity: int
        dev: bool
        family: str
        name: str
        size: str
        tier: Literal[Hyperscale]


    class azure.mgmt.azurearcdata.types.PostgresInstanceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('PostgresInstanceProperties', module='types')
        properties: PostgresInstanceProperties
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurearcdata.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurearcdata.types.Schedule(TypedDict, total=False):
        key "cronTrigger": ForwardRef('CronTrigger', module='types')
        key "enabled": bool
        cron_trigger: CronTrigger
        enabled: bool


    class azure.mgmt.azurearcdata.types.SequencerAction(TypedDict, total=False):
        key "actionId": str
        key "result": Union[str, Result]
        key "state": Union[str, SequencerState]
        action_id: str
        result: Union[str, Result]
        state: Union[str, SequencerState]


    class azure.mgmt.azurearcdata.types.ServerAssessmentsItem(TypedDict, total=False):
        key "appliesToMigrationTargetPlatform": str
        key "featureId": str
        key "issueCategory": str
        key "moreInformation": str
        applies_to_migration_target_platform: str
        feature_id: str
        impactedObjects: list[ServerAssessmentsPropertiesItemsItem]
        impacted_objects: list[ServerAssessmentsPropertiesItemsItem]
        issue_category: str
        more_information: str


    class azure.mgmt.azurearcdata.types.ServerAssessmentsPropertiesItemsItem(TypedDict, total=False):
        key "impactDetail": str
        key "name": str
        key "objectType": str
        impact_detail: str
        name: str
        object_type: str


    class azure.mgmt.azurearcdata.types.SkuRecommendationResults(TypedDict, total=False):
        key "azureSqlDatabase": ForwardRef('SkuRecommendationResultsAzureSqlDatabase', module='types')
        key "azureSqlManagedInstance": ForwardRef('SkuRecommendationResultsAzureSqlManagedInstance', module='types')
        key "azureSqlVirtualMachine": ForwardRef('SkuRecommendationResultsAzureSqlVirtualMachine', module='types')
        azure_sql_database: SkuRecommendationResultsAzureSqlDatabase
        azure_sql_managed_instance: SkuRecommendationResultsAzureSqlManagedInstance
        azure_sql_virtual_machine: SkuRecommendationResultsAzureSqlVirtualMachine


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlDatabase(TypedDict, total=False):
        key "monthlyCost": ForwardRef('SkuRecommendationResultsMonthlyCost', module='types')
        key "numberOfServerBlockerIssues": int
        key "recommendationStatus": Union[str, RecommendationStatus]
        key "targetSku": ForwardRef('SkuRecommendationResultsAzureSqlDatabaseTargetSku', module='types')
        monthlyCostOptions: list[SkuRecommendationResultsMonthlyCostOptionItem]
        monthly_cost: SkuRecommendationResultsMonthlyCost
        monthly_cost_options: list[SkuRecommendationResultsMonthlyCostOptionItem]
        number_of_server_blocker_issues: int
        recommendation_status: Union[str, RecommendationStatus]
        target_sku: SkuRecommendationResultsAzureSqlDatabaseTargetSku


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlDatabaseTargetSku(TypedDict, total=False):
        key "category": ForwardRef('SkuRecommendationResultsAzureSqlDatabaseTargetSkuCategory', module='types')
        key "computeSize": int
        key "maxStorageIops": float
        key "maxThroughputMBps": float
        key "predictedDataSizeInMb": float
        key "predictedLogSizeInMb": float
        key "storageMaxSizeInMb": float
        category: SkuRecommendationResultsAzureSqlDatabaseTargetSkuCategory
        compute_size: int
        max_storage_iops: float
        max_throughput_m_bps: float
        predicted_data_size_in_mb: float
        predicted_log_size_in_mb: float
        storage_max_size_in_mb: float


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlDatabaseTargetSkuCategory(TypedDict, total=False):
        key "computeTier": str
        key "hardwareType": str
        key "sqlPurchasingModel": str
        key "sqlServiceTier": str
        key "zoneRedundancyAvailable": bool
        compute_tier: str
        hardware_type: str
        sql_purchasing_model: str
        sql_service_tier: str
        zone_redundancy_available: bool


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlManagedInstance(TypedDict, total=False):
        key "monthlyCost": ForwardRef('SkuRecommendationResultsMonthlyCost', module='types')
        key "numberOfServerBlockerIssues": int
        key "recommendationStatus": Union[str, RecommendationStatus]
        key "targetSku": ForwardRef('SkuRecommendationResultsAzureSqlManagedInstanceTargetSku', module='types')
        monthlyCostOptions: list[SkuRecommendationResultsMonthlyCostOptionItem]
        monthly_cost: SkuRecommendationResultsMonthlyCost
        monthly_cost_options: list[SkuRecommendationResultsMonthlyCostOptionItem]
        number_of_server_blocker_issues: int
        recommendation_status: Union[str, RecommendationStatus]
        target_sku: SkuRecommendationResultsAzureSqlManagedInstanceTargetSku


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlManagedInstanceTargetSku(TypedDict, total=False):
        key "category": ForwardRef('SkuRecommendationResultsAzureSqlManagedInstanceTargetSkuCategory', module='types')
        key "computeSize": int
        key "maxStorageIops": float
        key "maxThroughputMBps": float
        key "predictedDataSizeInMb": float
        key "predictedLogSizeInMb": float
        key "storageMaxSizeInMb": float
        category: SkuRecommendationResultsAzureSqlManagedInstanceTargetSkuCategory
        compute_size: int
        max_storage_iops: float
        max_throughput_m_bps: float
        predicted_data_size_in_mb: float
        predicted_log_size_in_mb: float
        storage_max_size_in_mb: float


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlManagedInstanceTargetSkuCategory(TypedDict, total=False):
        key "computeTier": str
        key "hardwareType": str
        key "sqlPurchasingModel": str
        key "sqlServiceTier": str
        key "zoneRedundancyAvailable": bool
        compute_tier: str
        hardware_type: str
        sql_purchasing_model: str
        sql_service_tier: str
        zone_redundancy_available: bool


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlVirtualMachine(TypedDict, total=False):
        key "monthlyCost": ForwardRef('SkuRecommendationResultsMonthlyCost', module='types')
        key "numberOfServerBlockerIssues": int
        key "recommendationStatus": Union[str, RecommendationStatus]
        key "targetSku": ForwardRef('SkuRecommendationResultsAzureSqlVirtualMachineTargetSku', module='types')
        monthlyCostOptions: list[SkuRecommendationResultsMonthlyCostOptionItem]
        monthly_cost: SkuRecommendationResultsMonthlyCost
        monthly_cost_options: list[SkuRecommendationResultsMonthlyCostOptionItem]
        number_of_server_blocker_issues: int
        recommendation_status: Union[str, RecommendationStatus]
        target_sku: SkuRecommendationResultsAzureSqlVirtualMachineTargetSku


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlVirtualMachineTargetSku(TypedDict, total=False):
        key "category": ForwardRef('SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuCategory', module='types')
        key "computeSize": int
        key "predictedDataSizeInMb": float
        key "predictedLogSizeInMb": float
        key "virtualMachineSize": ForwardRef('SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuVirtualMachineSize', module='types')
        category: SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuCategory
        compute_size: int
        dataDiskSizes: list[DiskSizes]
        data_disk_sizes: list[DiskSizes]
        logDiskSizes: list[DiskSizes]
        log_disk_sizes: list[DiskSizes]
        predicted_data_size_in_mb: float
        predicted_log_size_in_mb: float
        tempDbDiskSizes: list[DiskSizes]
        temp_db_disk_sizes: list[DiskSizes]
        virtual_machine_size: SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuVirtualMachineSize


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuCategory(TypedDict, total=False):
        key "virtualMachineFamily": str
        availableVmSkus: list[str]
        available_vm_skus: list[str]
        virtual_machine_family: str


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsAzureSqlVirtualMachineTargetSkuVirtualMachineSize(TypedDict, total=False):
        key "azureSkuName": str
        key "computeSize": int
        key "maxNetworkInterfaces": int
        key "sizeName": str
        key "vCPUsAvailable": int
        key "virtualMachineFamily": str
        azure_sku_name: str
        compute_size: int
        max_network_interfaces: int
        size_name: str
        v_cpus_available: int
        virtual_machine_family: str


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsMonthlyCost(TypedDict, total=False):
        key "computeCost": float
        key "iopsCost": float
        key "sqlLicenseCost": float
        key "storageCost": float
        key "totalCost": float
        key "windowsLicenseCost": float
        compute_cost: float
        iops_cost: float
        sql_license_cost: float
        storage_cost: float
        total_cost: float
        windows_license_cost: float


    class azure.mgmt.azurearcdata.types.SkuRecommendationResultsMonthlyCostOptionItem(TypedDict, total=False):
        key "keyName": str
        key "keyValue": ForwardRef('CostTypeValues', module='types')
        key_name: str
        key_value: CostTypeValues


    class azure.mgmt.azurearcdata.types.SkuRecommendationSummary(TypedDict, total=False):
        key "monthlyCost": ForwardRef('SkuRecommendationResultsMonthlyCost', module='types')
        key "numOfBlockerIssues": int
        key "recommendationStatus": Union[str, RecommendationStatus]
        key "targetSku": ForwardRef('SkuRecommendationSummaryTargetSku', module='types')
        impactedObjectsSummary: list[ImpactedObjectsInfo]
        impacted_objects_summary: list[ImpactedObjectsInfo]
        monthlyCostOptions: list[SkuRecommendationResultsMonthlyCostOptionItem]
        monthly_cost: SkuRecommendationResultsMonthlyCost
        monthly_cost_options: list[SkuRecommendationResultsMonthlyCostOptionItem]
        num_of_blocker_issues: int
        recommendation_status: Union[str, RecommendationStatus]
        target_sku: SkuRecommendationSummaryTargetSku


    class azure.mgmt.azurearcdata.types.SkuRecommendationSummaryTargetSku(TypedDict, total=False):
        key "category": ForwardRef('SkuRecommendationSummaryTargetSkuCategory', module='types')
        key "computeSize": int
        key "maxStorageIops": float
        key "maxThroughputMBps": float
        key "predictedDataSizeInMb": float
        key "predictedLogSizeInMb": float
        key "storageMaxSizeInMb": float
        category: SkuRecommendationSummaryTargetSkuCategory
        compute_size: int
        max_storage_iops: float
        max_throughput_m_bps: float
        predicted_data_size_in_mb: float
        predicted_log_size_in_mb: float
        storage_max_size_in_mb: float


    class azure.mgmt.azurearcdata.types.SkuRecommendationSummaryTargetSkuCategory(TypedDict, total=False):
        key "computeTier": str
        key "hardwareType": str
        key "sqlPurchasingModel": str
        key "sqlServiceTier": str
        key "zoneRedundancyAvailable": bool
        compute_tier: str
        hardware_type: str
        sql_purchasing_model: str
        sql_service_tier: str
        zone_redundancy_available: bool


    class azure.mgmt.azurearcdata.types.SqlAvailabilityGroupDatabaseReplicaResourceProperties(TypedDict, total=False):
        key "databaseName": str
        key "databaseStateDescription": str
        key "isCommitParticipant": bool
        key "isLocal": bool
        key "isPrimaryReplica": bool
        key "isSuspended": bool
        key "replicaName": str
        key "suspendReasonDescription": str
        key "synchronizationHealthDescription": str
        key "synchronizationStateDescription": str
        database_name: str
        database_state_description: str
        is_commit_participant: bool
        is_local: bool
        is_primary_replica: bool
        is_suspended: bool
        replica_name: str
        suspend_reason_description: str
        synchronization_health_description: str
        synchronization_state_description: str


    class azure.mgmt.azurearcdata.types.SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem(TypedDict, total=False):
        key "ipAddress": str
        key "mask": str
        ip_address: str
        mask: str


    class azure.mgmt.azurearcdata.types.SqlAvailabilityGroupReplicaResourceProperties(TypedDict, total=False):
        key "configure": ForwardRef('AvailabilityGroupConfigure', module='types')
        key "replicaId": str
        key "replicaName": str
        key "replicaResourceId": str
        key "state": ForwardRef('AvailabilityGroupState', module='types')
        configure: AvailabilityGroupConfigure
        replica_id: str
        replica_name: str
        replica_resource_id: str
        state: AvailabilityGroupState


    class azure.mgmt.azurearcdata.types.SqlAvailabilityGroupStaticIPListenerProperties(TypedDict, total=False):
        key "dnsName": str
        key "port": int
        dns_name: str
        ipV4AddressesAndMasks: list[SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem]
        ipV6Addresses: list[str]
        ip_v4_addresses_and_masks: list[SqlAvailabilityGroupIpV4AddressesAndMasksPropertiesItem]
        ip_v6_addresses: list[str]
        port: int


    class azure.mgmt.azurearcdata.types.SqlManagedInstance(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[SqlManagedInstanceProperties]
        key "sku": ForwardRef('SqlManagedInstanceSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: SqlManagedInstanceProperties
        sku: SqlManagedInstanceSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.SqlManagedInstanceK8SRaw(TypedDict, total=False):
        key "spec": ForwardRef('SqlManagedInstanceK8SSpec', module='types')
        spec: SqlManagedInstanceK8SSpec


    class azure.mgmt.azurearcdata.types.SqlManagedInstanceK8SSpec(TypedDict, total=False):
        key "replicas": int
        key "scheduling": ForwardRef('K8SScheduling', module='types')
        key "security": ForwardRef('K8SSecurity', module='types')
        key "settings": ForwardRef('K8SSettings', module='types')
        replicas: int
        scheduling: K8SScheduling
        security: K8SSecurity
        settings: K8SSettings


    class azure.mgmt.azurearcdata.types.SqlManagedInstanceProperties(TypedDict, total=False):
        key "activeDirectoryInformation": ForwardRef('ActiveDirectoryInformation', module='types')
        key "admin": str
        key "basicLoginInformation": ForwardRef('BasicLoginInformation', module='types')
        key "clusterId": str
        key "dataControllerId": str
        key "endTime": str
        key "extensionId": str
        key "k8sRaw": ForwardRef('SqlManagedInstanceK8SRaw', module='types')
        key "lastUploadedDate": str
        key "licenseType": Union[str, ArcSqlManagedInstanceLicenseType]
        key "provisioningState": str
        key "startTime": str
        active_directory_information: ActiveDirectoryInformation
        admin: str
        basic_login_information: BasicLoginInformation
        cluster_id: str
        data_controller_id: str
        end_time: str
        extension_id: str
        k8_s_raw: SqlManagedInstanceK8SRaw
        last_uploaded_date: str
        license_type: Union[str, ArcSqlManagedInstanceLicenseType]
        provisioning_state: str
        start_time: str


    class azure.mgmt.azurearcdata.types.SqlManagedInstanceSku(TypedDict, total=False):
        key "capacity": int
        key "dev": bool
        key "family": str
        key "name": Required[Literal["vCore"]]
        key "size": str
        key "tier": Union[str, SqlManagedInstanceSkuTier]
        capacity: int
        dev: bool
        family: str
        name: Literal[vCore]
        size: str
        tier: Union[str, SqlManagedInstanceSkuTier]


    class azure.mgmt.azurearcdata.types.SqlManagedInstanceUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.SqlServerAvailabilityGroupResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[SqlServerAvailabilityGroupResourceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SqlServerAvailabilityGroupResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.SqlServerAvailabilityGroupResourceProperties(TypedDict, total=False):
        key "availabilityGroupId": str
        key "collectionTimestamp": str
        key "databases": ForwardRef('SqlServerAvailabilityGroupResourcePropertiesDatabases', module='types')
        key "info": ForwardRef('AvailabilityGroupInfo', module='types')
        key "instanceName": str
        key "provisioningState": str
        key "replicas": ForwardRef('SqlServerAvailabilityGroupResourcePropertiesReplicas', module='types')
        key "serverName": str
        key "vmId": str
        availability_group_id: str
        collection_timestamp: str
        databases: SqlServerAvailabilityGroupResourcePropertiesDatabases
        info: AvailabilityGroupInfo
        instance_name: str
        provisioning_state: str
        replicas: SqlServerAvailabilityGroupResourcePropertiesReplicas
        server_name: str
        vm_id: str


    class azure.mgmt.azurearcdata.types.SqlServerAvailabilityGroupResourcePropertiesDatabases(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[SqlAvailabilityGroupDatabaseReplicaResourceProperties]


    class azure.mgmt.azurearcdata.types.SqlServerAvailabilityGroupResourcePropertiesReplicas(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[SqlAvailabilityGroupReplicaResourceProperties]


    class azure.mgmt.azurearcdata.types.SqlServerAvailabilityGroupUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SqlServerAvailabilityGroupResourceProperties', module='types')
        properties: SqlServerAvailabilityGroupResourceProperties
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.SqlServerDatabaseResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[SqlServerDatabaseResourceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SqlServerDatabaseResourceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.SqlServerDatabaseResourceProperties(TypedDict, total=False):
        key "backupInformation": ForwardRef('SqlServerDatabaseResourcePropertiesBackupInformation', module='types')
        key "backupPolicy": ForwardRef('BackupPolicy', module='types')
        key "collationName": str
        key "compatibilityLevel": int
        key "createMode": Union[str, DatabaseCreateMode]
        key "dataFileSizeMB": float
        key "databaseCreationDate": str
        key "databaseOptions": ForwardRef('SqlServerDatabaseResourcePropertiesDatabaseOptions', module='types')
        key "earliestRestoreDate": str
        key "isReadOnly": bool
        key "lastDatabaseUploadTime": str
        key "logFileSizeMB": float
        key "migration": ForwardRef('DataBaseMigration', module='types')
        key "provisioningState": str
        key "recoveryMode": Union[str, RecoveryMode]
        key "restorePointInTime": str
        key "sizeMB": float
        key "sourceDatabaseId": str
        key "spaceAvailableMB": float
        key "state": Union[str, DatabaseState]
        key "vmId": str
        backup_information: SqlServerDatabaseResourcePropertiesBackupInformation
        backup_policy: BackupPolicy
        collation_name: str
        compatibility_level: int
        create_mode: Union[str, DatabaseCreateMode]
        data_file_size_mb: float
        database_creation_date: str
        database_options: SqlServerDatabaseResourcePropertiesDatabaseOptions
        earliest_restore_date: str
        is_read_only: bool
        last_database_upload_time: str
        log_file_size_mb: float
        migration: DataBaseMigration
        provisioning_state: str
        recovery_mode: Union[str, RecoveryMode]
        restore_point_in_time: str
        size_mb: float
        source_database_id: str
        space_available_mb: float
        state: Union[str, DatabaseState]
        vm_id: str


    class azure.mgmt.azurearcdata.types.SqlServerDatabaseResourcePropertiesBackupInformation(TypedDict, total=False):
        key "lastFullBackup": str
        key "lastLogBackup": str
        last_full_backup: str
        last_log_backup: str


    class azure.mgmt.azurearcdata.types.SqlServerDatabaseResourcePropertiesDatabaseOptions(TypedDict, total=False):
        key "isAutoCloseOn": bool
        key "isAutoCreateStatsOn": bool
        key "isAutoShrinkOn": bool
        key "isAutoUpdateStatsOn": bool
        key "isEncrypted": bool
        key "isHekatonFilesOn": bool
        key "isMemoryOptimizationEnabled": bool
        key "isRemoteDataArchiveEnabled": bool
        key "isTrustworthyOn": bool
        key "numberOfHekatonFiles": int
        is_auto_close_on: bool
        is_auto_create_stats_on: bool
        is_auto_shrink_on: bool
        is_auto_update_stats_on: bool
        is_encrypted: bool
        is_hekaton_files_on: bool
        is_memory_optimization_enabled: bool
        is_remote_data_archive_enabled: bool
        is_trustworthy_on: bool
        number_of_hekaton_files: int


    class azure.mgmt.azurearcdata.types.SqlServerDatabaseUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SqlServerDatabaseResourceProperties', module='types')
        properties: SqlServerDatabaseResourceProperties
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.SqlServerEsuLicense(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[SqlServerEsuLicenseProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SqlServerEsuLicenseProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.SqlServerEsuLicenseProperties(TypedDict, total=False):
        key "activatedAt": str
        key "activationState": Required[Union[str, State]]
        key "billingPlan": Required[Union[str, BillingPlan]]
        key "physicalCores": Required[int]
        key "scopeType": Required[Union[str, ScopeType]]
        key "tenantId": str
        key "terminatedAt": str
        key "uniqueId": str
        key "version": Required[Union[str, Version]]
        activated_at: str
        activation_state: Union[str, State]
        billing_plan: Union[str, BillingPlan]
        physical_cores: int
        scope_type: Union[str, ScopeType]
        tenant_id: str
        terminated_at: str
        unique_id: str
        version: Union[str, Version]


    class azure.mgmt.azurearcdata.types.SqlServerEsuLicenseUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SqlServerEsuLicenseUpdateProperties', module='types')
        properties: SqlServerEsuLicenseUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.SqlServerEsuLicenseUpdateProperties(TypedDict, total=False):
        key "activatedAt": str
        key "activationState": Union[str, State]
        key "billingPlan": Union[str, BillingPlan]
        key "physicalCores": int
        key "scopeType": Union[str, ScopeType]
        key "tenantId": str
        key "terminatedAt": str
        key "uniqueId": str
        key "version": Union[str, Version]
        activated_at: str
        activation_state: Union[str, State]
        billing_plan: Union[str, BillingPlan]
        physical_cores: int
        scope_type: Union[str, ScopeType]
        tenant_id: str
        terminated_at: str
        unique_id: str
        version: Union[str, Version]


    class azure.mgmt.azurearcdata.types.SqlServerInstance(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SqlServerInstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SqlServerInstanceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceBpaColumn(TypedDict, total=False):
        key "name": str
        key "type": Union[str, SqlServerInstanceBpaColumnType]
        name: str
        type: Union[str, SqlServerInstanceBpaColumnType]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceBpaRequest(TypedDict, total=False):
        key "queryType": Union[str, SqlServerInstanceBpaQueryType]
        key "reportId": str
        key "reportType": Union[str, SqlServerInstanceBpaReportType]
        key "skipToken": str
        query_type: Union[str, SqlServerInstanceBpaQueryType]
        report_id: str
        report_type: Union[str, SqlServerInstanceBpaReportType]
        skip_token: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceJob(TypedDict, total=False):
        key "backgroundJob": ForwardRef('BackgroundJob', module='types')
        key "id": str
        key "instanceName": str
        key "jobException": str
        key "jobStatus": Union[str, JobStatus]
        background_job: BackgroundJob
        id: str
        instance_name: str
        job_exception: str
        job_status: Union[str, JobStatus]
        sequencerActions: list[SequencerAction]
        sequencer_actions: list[SequencerAction]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceJobStatus(TypedDict, total=False):
        key "backgroundJob": ForwardRef('BackgroundJob', module='types')
        key "id": str
        key "instanceName": str
        key "jobException": str
        key "jobStatus": Union[str, JobStatus]
        background_job: BackgroundJob
        id: str
        instance_name: str
        job_exception: str
        job_status: Union[str, JobStatus]
        sequencerActions: list[SequencerAction]
        sequencer_actions: list[SequencerAction]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceJobsRequest(TypedDict, total=False):
        key "featureName": str
        key "jobType": str
        feature_name: str
        job_type: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceJobsResponse(TypedDict, total=False):
        jobs: list[SqlServerInstanceJob]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceJobsStatusRequest(TypedDict, total=False):
        key "featureName": str
        key "jobType": str
        feature_name: str
        job_type: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceJobsStatusResponse(TypedDict, total=False):
        jobsStatus: list[SqlServerInstanceJobStatus]
        jobs_status: list[SqlServerInstanceJobStatus]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceManagedInstanceLinkAssessment(TypedDict, total=False):
        key "additionalInformation": str
        key "category": Union[str, MiLinkAssessmentCategory]
        key "information": str
        key "name": str
        key "status": Union[str, AssessmentStatus]
        additional_information: str
        category: Union[str, MiLinkAssessmentCategory]
        failingDbs: list[str]
        failing_dbs: list[str]
        information: str
        name: str
        status: Union[str, AssessmentStatus]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceManagedInstanceLinkAssessmentRequest(TypedDict, total=False):
        key "availabilityGroupName": Required[str]
        key "azureManagedInstanceResourceId": Required[str]
        key "azureManagedInstanceRole": Union[str, AzureManagedInstanceRole]
        key "databaseNames": Required[list[str]]
        key "distributedAvailabilityGroupName": Required[str]
        key "sqlServerIpAddress": str
        assessmentCategories: list[Union[str, MiLinkAssessmentCategory]]
        assessment_categories: list[Union[str, MiLinkAssessmentCategory]]
        availability_group_name: str
        azure_managed_instance_resource_id: str
        azure_managed_instance_role: Union[str, AzureManagedInstanceRole]
        database_names: list[str]
        distributed_availability_group_name: str
        sql_server_ip_address: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceManagedInstanceLinkAssessmentResponse(TypedDict, total=False):
        assessments: list[SqlServerInstanceManagedInstanceLinkAssessment]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceMigrationReadinessReportResponse(TypedDict, total=False):
        key "createdTime": str
        key "isCompressed": bool
        key "report": str
        created_time: str
        is_compressed: bool
        report: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceProperties(TypedDict, total=False):
        key "alwaysOnRole": Union[str, AlwaysOnRole]
        key "authentication": ForwardRef('Authentication', module='types')
        key "azureDefenderStatus": Union[str, DefenderStatus]
        key "azureDefenderStatusLastUpdated": str
        key "backupPolicy": ForwardRef('BackupPolicy', module='types')
        key "bestPracticesAssessment": ForwardRef('BestPracticesAssessment', module='types')
        key "clientConnection": ForwardRef('ClientConnection', module='types')
        key "collation": str
        key "containerResourceId": str
        key "cores": str
        key "createTime": str
        key "currentVersion": str
        key "databaseMirroringEndpoint": ForwardRef('DBMEndpoint', module='types')
        key "dbMasterKeyExists": bool
        key "discoverySource": Union[str, DiscoverySource]
        key "edition": Union[str, EditionType]
        key "failoverCluster": ForwardRef('FailoverCluster', module='types')
        key "hostType": Union[str, HostType]
        key "instanceName": str
        key "isDigiCertPkiCertTrustConfigured": bool
        key "isHadrEnabled": bool
        key "isMicrosoftPkiCertTrustConfigured": bool
        key "lastInventoryUploadTime": str
        key "lastUsageUploadTime": str
        key "licenseType": Union[str, ArcSqlServerLicenseType]
        key "maxServerMemoryMB": int
        key "migration": ForwardRef('Migration', module='types')
        key "monitoring": ForwardRef('Monitoring', module='types')
        key "patchLevel": str
        key "productId": str
        key "provisioningState": str
        key "serviceType": Union[str, ServiceType]
        key "status": Union[str, ConnectionStatus]
        key "tcpDynamicPorts": str
        key "tcpStaticPorts": str
        key "upgradeLockedUntil": str
        key "vCore": str
        key "version": Union[str, SqlVersion]
        key "vmId": str
        always_on_role: Union[str, AlwaysOnRole]
        authentication: Authentication
        azure_defender_status: Union[str, DefenderStatus]
        azure_defender_status_last_updated: str
        backup_policy: BackupPolicy
        best_practices_assessment: BestPracticesAssessment
        client_connection: ClientConnection
        collation: str
        container_resource_id: str
        cores: str
        create_time: str
        current_version: str
        database_mirroring_endpoint: DBMEndpoint
        db_master_key_exists: bool
        discovery_source: Union[str, DiscoverySource]
        edition: Union[str, EditionType]
        failover_cluster: FailoverCluster
        host_type: Union[str, HostType]
        instance_name: str
        is_digi_cert_pki_cert_trust_configured: bool
        is_hadr_enabled: bool
        is_microsoft_pki_cert_trust_configured: bool
        last_inventory_upload_time: str
        last_usage_upload_time: str
        license_type: Union[str, ArcSqlServerLicenseType]
        max_server_memory_mb: int
        migration: Migration
        monitoring: Monitoring
        patch_level: str
        product_id: str
        provisioning_state: str
        service_type: Union[str, ServiceType]
        status: Union[str, ConnectionStatus]
        tcp_dynamic_ports: str
        tcp_static_ports: str
        traceFlags: list[int]
        trace_flags: list[int]
        upgrade_locked_until: str
        v_core: str
        version: Union[str, SqlVersion]
        vm_id: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceRunBestPracticesAssessmentResponse(TypedDict, total=False):
        key "backgroundJob": ForwardRef('BackgroundJob', module='types')
        key "id": str
        key "instanceName": str
        key "jobException": str
        key "jobStatus": Union[str, JobStatus]
        background_job: BackgroundJob
        id: str
        instance_name: str
        job_exception: str
        job_status: Union[str, JobStatus]
        sequencerActions: list[SequencerAction]
        sequencer_actions: list[SequencerAction]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceRunMigrationAssessmentResponse(TypedDict, total=False):
        key "backgroundJob": ForwardRef('BackgroundJob', module='types')
        key "id": str
        key "instanceName": str
        key "jobException": str
        key "jobStatus": Union[str, JobStatus]
        background_job: BackgroundJob
        id: str
        instance_name: str
        job_exception: str
        job_status: Union[str, JobStatus]
        sequencerActions: list[SequencerAction]
        sequencer_actions: list[SequencerAction]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceRunMigrationReadinessAssessmentResponse(TypedDict, total=False):
        key "backgroundJob": ForwardRef('BackgroundJob', module='types')
        key "id": str
        key "instanceName": str
        key "jobException": str
        key "jobStatus": Union[str, JobStatus]
        background_job: BackgroundJob
        id: str
        instance_name: str
        job_exception: str
        job_status: Union[str, JobStatus]
        sequencerActions: list[SequencerAction]
        sequencer_actions: list[SequencerAction]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceRunTargetRecommendationJobRequest(TypedDict, total=False):
        key "includeFileLevelRequirements": bool
        key "lookbackPeriodInDays": int
        key "percentile": int
        key "resourceUpdateMode": Union[str, ResourceUpdateMode]
        key "targetLocation": str
        include_file_level_requirements: bool
        lookback_period_in_days: int
        percentile: int
        resource_update_mode: Union[str, ResourceUpdateMode]
        target_location: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceRunTargetRecommendationJobResponse(TypedDict, total=False):
        key "jobStatus": Union[str, JobStatus]
        job_status: Union[str, JobStatus]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceTargetRecommendationReport(TypedDict, total=False):
        key "createdTime": str
        key "reportId": str
        created_time: str
        report_id: str
        sections: list[SqlServerInstanceTargetRecommendationReportSection]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceTargetRecommendationReportSection(TypedDict, total=False):
        key "data": str
        key "databaseName": str
        key "isCompressed": bool
        key "type": Union[str, SqlServerInstanceTargetRecommendationReportSectionType]
        data: str
        database_name: str
        is_compressed: bool
        type: Union[str, SqlServerInstanceTargetRecommendationReportSectionType]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceTargetRecommendationReportsRequest(TypedDict, total=False):
        key "reportOffset": int
        key "sectionOffset": int
        key "sectionType": Union[str, SqlServerInstanceTargetRecommendationReportSectionType]
        databaseNames: list[str]
        database_names: list[str]
        report_offset: int
        section_offset: int
        section_type: Union[str, SqlServerInstanceTargetRecommendationReportSectionType]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceTargetRecommendationReportsResponse(TypedDict, total=False):
        key "jobStatus": Union[str, JobStatus]
        key "nextReportOffset": int
        key "nextSectionOffset": int
        key "totalReportCount": int
        job_status: Union[str, JobStatus]
        next_report_offset: int
        next_section_offset: int
        reports: list[SqlServerInstanceTargetRecommendationReport]
        total_report_count: int


    class azure.mgmt.azurearcdata.types.SqlServerInstanceTelemetryColumn(TypedDict, total=False):
        key "name": str
        key "type": Union[str, SqlServerInstanceTelemetryColumnType]
        name: str
        type: Union[str, SqlServerInstanceTelemetryColumnType]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceTelemetryRequest(TypedDict, total=False):
        key "aggregationType": Union[str, AggregationType]
        key "datasetName": Required[str]
        key "endTime": str
        key "interval": str
        key "startTime": str
        aggregation_type: Union[str, AggregationType]
        databaseNames: list[str]
        database_names: list[str]
        dataset_name: str
        end_time: str
        interval: str
        start_time: str


    class azure.mgmt.azurearcdata.types.SqlServerInstanceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SqlServerInstanceUpdateProperties', module='types')
        properties: SqlServerInstanceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.SqlServerInstanceUpdateProperties(TypedDict, total=False):
        key "alwaysOnRole": Union[str, AlwaysOnRole]
        key "authentication": ForwardRef('Authentication', module='types')
        key "azureDefenderStatus": Union[str, DefenderStatus]
        key "azureDefenderStatusLastUpdated": str
        key "backupPolicy": ForwardRef('BackupPolicy', module='types')
        key "bestPracticesAssessment": ForwardRef('BestPracticesAssessment', module='types')
        key "clientConnection": ForwardRef('ClientConnection', module='types')
        key "collation": str
        key "containerResourceId": str
        key "cores": str
        key "createTime": str
        key "currentVersion": str
        key "databaseMirroringEndpoint": ForwardRef('DBMEndpoint', module='types')
        key "dbMasterKeyExists": bool
        key "discoverySource": Union[str, DiscoverySource]
        key "edition": Union[str, EditionType]
        key "failoverCluster": ForwardRef('FailoverCluster', module='types')
        key "hostType": Union[str, HostType]
        key "instanceName": str
        key "isDigiCertPkiCertTrustConfigured": bool
        key "isHadrEnabled": bool
        key "isMicrosoftPkiCertTrustConfigured": bool
        key "lastInventoryUploadTime": str
        key "lastUsageUploadTime": str
        key "licenseType": Union[str, ArcSqlServerLicenseType]
        key "maxServerMemoryMB": int
        key "migration": ForwardRef('Migration', module='types')
        key "monitoring": ForwardRef('Monitoring', module='types')
        key "patchLevel": str
        key "productId": str
        key "provisioningState": str
        key "serviceType": Union[str, ServiceType]
        key "status": Union[str, ConnectionStatus]
        key "tcpDynamicPorts": str
        key "tcpStaticPorts": str
        key "upgradeLockedUntil": str
        key "vCore": str
        key "version": Union[str, SqlVersion]
        key "vmId": str
        always_on_role: Union[str, AlwaysOnRole]
        authentication: Authentication
        azure_defender_status: Union[str, DefenderStatus]
        azure_defender_status_last_updated: str
        backup_policy: BackupPolicy
        best_practices_assessment: BestPracticesAssessment
        client_connection: ClientConnection
        collation: str
        container_resource_id: str
        cores: str
        create_time: str
        current_version: str
        database_mirroring_endpoint: DBMEndpoint
        db_master_key_exists: bool
        discovery_source: Union[str, DiscoverySource]
        edition: Union[str, EditionType]
        failover_cluster: FailoverCluster
        host_type: Union[str, HostType]
        instance_name: str
        is_digi_cert_pki_cert_trust_configured: bool
        is_hadr_enabled: bool
        is_microsoft_pki_cert_trust_configured: bool
        last_inventory_upload_time: str
        last_usage_upload_time: str
        license_type: Union[str, ArcSqlServerLicenseType]
        max_server_memory_mb: int
        migration: Migration
        monitoring: Monitoring
        patch_level: str
        product_id: str
        provisioning_state: str
        service_type: Union[str, ServiceType]
        status: Union[str, ConnectionStatus]
        tcp_dynamic_ports: str
        tcp_static_ports: str
        traceFlags: list[int]
        trace_flags: list[int]
        upgrade_locked_until: str
        v_core: str
        version: Union[str, SqlVersion]
        vm_id: str


    class azure.mgmt.azurearcdata.types.SqlServerLicense(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[SqlServerLicenseProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SqlServerLicenseProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.SqlServerLicenseProperties(TypedDict, total=False):
        key "activationState": Required[Union[str, ActivationState]]
        key "billingPlan": Required[Union[str, BillingPlan]]
        key "lastActivatedAt": str
        key "lastDeactivatedAt": str
        key "licenseCategory": Required[Union[str, LicenseCategory]]
        key "physicalCores": Required[int]
        key "scopeType": Required[Union[str, ScopeType]]
        key "tenantId": str
        activation_state: Union[str, ActivationState]
        billing_plan: Union[str, BillingPlan]
        last_activated_at: str
        last_deactivated_at: str
        license_category: Union[str, LicenseCategory]
        physical_cores: int
        scope_type: Union[str, ScopeType]
        tenant_id: str


    class azure.mgmt.azurearcdata.types.SqlServerLicenseUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SqlServerLicenseUpdateProperties', module='types')
        properties: SqlServerLicenseUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.azurearcdata.types.SqlServerLicenseUpdateProperties(TypedDict, total=False):
        key "activationState": Union[str, ActivationState]
        key "billingPlan": Union[str, BillingPlan]
        key "lastActivatedAt": str
        key "lastDeactivatedAt": str
        key "licenseCategory": Union[str, LicenseCategory]
        key "physicalCores": int
        key "scopeType": Union[str, ScopeType]
        key "tenantId": str
        activation_state: Union[str, ActivationState]
        billing_plan: Union[str, BillingPlan]
        last_activated_at: str
        last_deactivated_at: str
        license_category: Union[str, LicenseCategory]
        physical_cores: int
        scope_type: Union[str, ScopeType]
        tenant_id: str


    class azure.mgmt.azurearcdata.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.azurearcdata.types.TargetReadiness(TypedDict, total=False):
        key "azureSqlDatabase": ForwardRef('SkuRecommendationSummary', module='types')
        key "azureSqlManagedInstance": ForwardRef('SkuRecommendationSummary', module='types')
        key "azureSqlVirtualMachine": ForwardRef('SkuRecommendationSummary', module='types')
        azure_sql_database: SkuRecommendationSummary
        azure_sql_managed_instance: SkuRecommendationSummary
        azure_sql_virtual_machine: SkuRecommendationSummary


    class azure.mgmt.azurearcdata.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurearcdata.types.UploadServicePrincipal(TypedDict, total=False):
        key "authority": str
        key "clientId": str
        key "clientSecret": str
        key "tenantId": str
        authority: str
        client_id: str
        client_secret: str
        tenant_id: str


    class azure.mgmt.azurearcdata.types.UploadWatermark(TypedDict, total=False):
        key "logs": str
        key "metrics": str
        key "usages": str
        logs: str
        metrics: str
        usages: str


```