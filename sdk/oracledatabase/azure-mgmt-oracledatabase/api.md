```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.oracledatabase

    class azure.mgmt.oracledatabase.OracleDatabaseMgmtClient: implements ContextManager 
        autonomous_database_backups: AutonomousDatabaseBackupsOperations
        autonomous_database_character_sets: AutonomousDatabaseCharacterSetsOperations
        autonomous_database_national_character_sets: AutonomousDatabaseNationalCharacterSetsOperations
        autonomous_database_versions: AutonomousDatabaseVersionsOperations
        autonomous_databases: AutonomousDatabasesOperations
        cloud_exadata_infrastructures: CloudExadataInfrastructuresOperations
        cloud_vm_clusters: CloudVmClustersOperations
        db_nodes: DbNodesOperations
        db_servers: DbServersOperations
        db_system_shapes: DbSystemShapesOperations
        db_systems: DbSystemsOperations
        db_versions: DbVersionsOperations
        dns_private_views: DnsPrivateViewsOperations
        dns_private_zones: DnsPrivateZonesOperations
        exadb_vm_clusters: ExadbVmClustersOperations
        exascale_db_nodes: ExascaleDbNodesOperations
        exascale_db_storage_vaults: ExascaleDbStorageVaultsOperations
        flex_components: FlexComponentsOperations
        gi_minor_versions: GiMinorVersionsOperations
        gi_versions: GiVersionsOperations
        network_anchors: NetworkAnchorsOperations
        operations: Operations
        oracle_subscriptions: OracleSubscriptionsOperations
        resource_anchors: ResourceAnchorsOperations
        system_versions: SystemVersionsOperations
        virtual_network_addresses: VirtualNetworkAddressesOperations

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


namespace azure.mgmt.oracledatabase.aio

    class azure.mgmt.oracledatabase.aio.OracleDatabaseMgmtClient: implements AsyncContextManager 
        autonomous_database_backups: AutonomousDatabaseBackupsOperations
        autonomous_database_character_sets: AutonomousDatabaseCharacterSetsOperations
        autonomous_database_national_character_sets: AutonomousDatabaseNationalCharacterSetsOperations
        autonomous_database_versions: AutonomousDatabaseVersionsOperations
        autonomous_databases: AutonomousDatabasesOperations
        cloud_exadata_infrastructures: CloudExadataInfrastructuresOperations
        cloud_vm_clusters: CloudVmClustersOperations
        db_nodes: DbNodesOperations
        db_servers: DbServersOperations
        db_system_shapes: DbSystemShapesOperations
        db_systems: DbSystemsOperations
        db_versions: DbVersionsOperations
        dns_private_views: DnsPrivateViewsOperations
        dns_private_zones: DnsPrivateZonesOperations
        exadb_vm_clusters: ExadbVmClustersOperations
        exascale_db_nodes: ExascaleDbNodesOperations
        exascale_db_storage_vaults: ExascaleDbStorageVaultsOperations
        flex_components: FlexComponentsOperations
        gi_minor_versions: GiMinorVersionsOperations
        gi_versions: GiVersionsOperations
        network_anchors: NetworkAnchorsOperations
        operations: Operations
        oracle_subscriptions: OracleSubscriptionsOperations
        resource_anchors: ResourceAnchorsOperations
        system_versions: SystemVersionsOperations
        virtual_network_addresses: VirtualNetworkAddressesOperations

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


namespace azure.mgmt.oracledatabase.aio.operations

    class azure.mgmt.oracledatabase.aio.operations.AutonomousDatabaseBackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                resource: AutonomousDatabaseBackup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabaseBackup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabaseBackup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabaseBackup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                properties: AutonomousDatabaseBackupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabaseBackup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabaseBackup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabaseBackup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                **kwargs: Any
            ) -> AutonomousDatabaseBackup: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutonomousDatabaseBackup]: ...


    class azure.mgmt.oracledatabase.aio.operations.AutonomousDatabaseCharacterSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                adbscharsetname: str, 
                **kwargs: Any
            ) -> AutonomousDatabaseCharacterSet: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutonomousDatabaseCharacterSet]: ...


    class azure.mgmt.oracledatabase.aio.operations.AutonomousDatabaseNationalCharacterSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                adbsncharsetname: str, 
                **kwargs: Any
            ) -> AutonomousDatabaseNationalCharacterSet: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutonomousDatabaseNationalCharacterSet]: ...


    class azure.mgmt.oracledatabase.aio.operations.AutonomousDatabaseVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                autonomousdbversionsname: str, 
                **kwargs: Any
            ) -> AutonomousDbVersion: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutonomousDbVersion]: ...


    class azure.mgmt.oracledatabase.aio.operations.AutonomousDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: AutonomousDatabaseLifecycleAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_change_disaster_recovery_configuration(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: DisasterRecoveryConfigurationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_change_disaster_recovery_configuration(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_change_disaster_recovery_configuration(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                resource: AutonomousDatabase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_failover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: PeerDbDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_failover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_failover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_restore(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: RestoreAutonomousDatabaseDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_restore(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_restore(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @distributed_trace_async
        async def begin_shrink(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_switchover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: PeerDbDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_switchover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_switchover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                properties: AutonomousDatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AutonomousDatabase]: ...

        @overload
        async def generate_wallet(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: GenerateAutonomousDatabaseWalletDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutonomousDatabaseWalletFile: ...

        @overload
        async def generate_wallet(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutonomousDatabaseWalletFile: ...

        @overload
        async def generate_wallet(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutonomousDatabaseWalletFile: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> AutonomousDatabase: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutonomousDatabase]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AutonomousDatabase]: ...


    class azure.mgmt.oracledatabase.aio.operations.CloudExadataInfrastructuresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_add_storage_capacity(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_configure_exascale(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                body: ConfigureExascaleCloudExadataInfrastructureDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_configure_exascale(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_configure_exascale(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                resource: CloudExadataInfrastructure, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                properties: CloudExadataInfrastructureUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudExadataInfrastructure]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> CloudExadataInfrastructure: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudExadataInfrastructure]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CloudExadataInfrastructure]: ...


    class azure.mgmt.oracledatabase.aio.operations.CloudVmClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: AddRemoveDbNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_add_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_add_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                resource: CloudVmCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: AddRemoveDbNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_remove_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_remove_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                properties: CloudVmClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudVmCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> CloudVmCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudVmCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CloudVmCluster]: ...

        @overload
        async def list_private_ip_addresses(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: PrivateIpAddressesFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[PrivateIpAddressProperties]: ...

        @overload
        async def list_private_ip_addresses(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[PrivateIpAddressProperties]: ...

        @overload
        async def list_private_ip_addresses(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[PrivateIpAddressProperties]: ...


    class azure.mgmt.oracledatabase.aio.operations.DbNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                body: DbNodeAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbNode]: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbNode]: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbNode]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                **kwargs: Any
            ) -> DbNode: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DbNode]: ...


    class azure.mgmt.oracledatabase.aio.operations.DbServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                dbserverocid: str, 
                **kwargs: Any
            ) -> DbServer: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DbServer]: ...


    class azure.mgmt.oracledatabase.aio.operations.DbSystemShapesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                dbsystemshapename: str, 
                **kwargs: Any
            ) -> DbSystemShape: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'zone', 'accept'], '2025-08-01-preview': ['shape_attribute']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_location(
                self, 
                location: str, 
                *, 
                shape_attribute: Optional[str] = ..., 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DbSystemShape]: ...


    class azure.mgmt.oracledatabase.aio.operations.DbSystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                resource: DbSystem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbSystem]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbSystem]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbSystem]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'db_system_name']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                properties: DbSystemUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbSystem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbSystem]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbSystem]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'db_system_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                **kwargs: Any
            ) -> DbSystem: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DbSystem]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[DbSystem]: ...


    class azure.mgmt.oracledatabase.aio.operations.DbVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'location', 'dbversionsname', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                location: str, 
                dbversionsname: str, 
                **kwargs: Any
            ) -> DbVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'location', 'db_system_shape', 'db_system_id', 'storage_management', 'is_upgrade_supported', 'is_database_software_image_supported', 'shape_family', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_location(
                self, 
                location: str, 
                *, 
                db_system_id: Optional[str] = ..., 
                db_system_shape: Optional[Union[str, BaseDbSystemShapes]] = ..., 
                is_database_software_image_supported: Optional[bool] = ..., 
                is_upgrade_supported: Optional[bool] = ..., 
                shape_family: Optional[Union[str, ShapeFamilyType]] = ..., 
                storage_management: Optional[Union[str, StorageManagementType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DbVersion]: ...


    class azure.mgmt.oracledatabase.aio.operations.DnsPrivateViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                dnsprivateviewocid: str, 
                **kwargs: Any
            ) -> DnsPrivateView: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsPrivateView]: ...


    class azure.mgmt.oracledatabase.aio.operations.DnsPrivateZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                dnsprivatezonename: str, 
                **kwargs: Any
            ) -> DnsPrivateZone: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DnsPrivateZone]: ...


    class azure.mgmt.oracledatabase.aio.operations.ExadbVmClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                resource: ExadbVmCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remove_vms(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                body: RemoveVirtualMachineFromExadbVmClusterDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @overload
        async def begin_remove_vms(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @overload
        async def begin_remove_vms(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                properties: ExadbVmClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExadbVmCluster]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                **kwargs: Any
            ) -> ExadbVmCluster: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExadbVmCluster]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ExadbVmCluster]: ...


    class azure.mgmt.oracledatabase.aio.operations.ExascaleDbNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                body: DbNodeAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbActionResponse]: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbActionResponse]: ...

        @overload
        async def begin_action(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DbActionResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name', 'exascale_db_node_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                **kwargs: Any
            ) -> ExascaleDbNode: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExascaleDbNode]: ...


    class azure.mgmt.oracledatabase.aio.operations.ExascaleDbStorageVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                resource: ExascaleDbStorageVault, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExascaleDbStorageVault]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExascaleDbStorageVault]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExascaleDbStorageVault]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exascale_db_storage_vault_name']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                properties: ExascaleDbStorageVaultTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExascaleDbStorageVault]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExascaleDbStorageVault]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExascaleDbStorageVault]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exascale_db_storage_vault_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                **kwargs: Any
            ) -> ExascaleDbStorageVault: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExascaleDbStorageVault]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ExascaleDbStorageVault]: ...


    class azure.mgmt.oracledatabase.aio.operations.FlexComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-01-01-preview', params_added_on={'2025-01-01-preview': ['api_version', 'subscription_id', 'location', 'flex_component_name', 'accept']}, api_versions_list=['2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                location: str, 
                flex_component_name: str, 
                **kwargs: Any
            ) -> FlexComponent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-01-01-preview', params_added_on={'2025-01-01-preview': ['api_version', 'subscription_id', 'location', 'shape', 'accept']}, api_versions_list=['2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                location: str, 
                *, 
                shape: Optional[Union[str, SystemShapes]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FlexComponent]: ...


    class azure.mgmt.oracledatabase.aio.operations.GiMinorVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'giversionname', 'gi_minor_version_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                location: str, 
                giversionname: str, 
                gi_minor_version_name: str, 
                **kwargs: Any
            ) -> GiMinorVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'giversionname', 'shape_family', 'zone', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                location: str, 
                giversionname: str, 
                *, 
                shape_family: Optional[Union[str, ShapeFamily]] = ..., 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GiMinorVersion]: ...


    class azure.mgmt.oracledatabase.aio.operations.GiVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                giversionname: str, 
                **kwargs: Any
            ) -> GiVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'shape', 'zone', 'accept'], '2025-08-01-preview': ['shape_attribute']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_location(
                self, 
                location: str, 
                *, 
                shape: Optional[Union[str, SystemShapes]] = ..., 
                shape_attribute: Optional[str] = ..., 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GiVersion]: ...


    class azure.mgmt.oracledatabase.aio.operations.NetworkAnchorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                resource: NetworkAnchor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkAnchor]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkAnchor]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkAnchor]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_anchor_name']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                properties: NetworkAnchorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkAnchor]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkAnchor]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkAnchor]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_anchor_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                **kwargs: Any
            ) -> NetworkAnchor: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetworkAnchor]: ...


    class azure.mgmt.oracledatabase.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.oracledatabase.aio.operations.OracleSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_add_azure_subscriptions(
                self, 
                body: AzureSubscriptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_azure_subscriptions(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_add_azure_subscriptions(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource: OracleSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OracleSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OracleSubscription]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OracleSubscription]: ...

        @distributed_trace_async
        async def begin_delete(self, **kwargs: Any) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_list_activation_links(self, **kwargs: Any) -> AsyncLROPoller[ActivationLinks]: ...

        @distributed_trace_async
        async def begin_list_cloud_account_details(self, **kwargs: Any) -> AsyncLROPoller[CloudAccountDetails]: ...

        @distributed_trace_async
        async def begin_list_saas_subscription_details(self, **kwargs: Any) -> AsyncLROPoller[SaasSubscriptionDetails]: ...

        @overload
        async def begin_update(
                self, 
                properties: OracleSubscriptionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OracleSubscription]: ...

        @overload
        async def begin_update(
                self, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OracleSubscription]: ...

        @overload
        async def begin_update(
                self, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OracleSubscription]: ...

        @distributed_trace_async
        async def get(self, **kwargs: Any) -> OracleSubscription: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[OracleSubscription]: ...


    class azure.mgmt.oracledatabase.aio.operations.ResourceAnchorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                resource: ResourceAnchor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceAnchor]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceAnchor]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceAnchor]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_anchor_name']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                properties: ResourceAnchorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceAnchor]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceAnchor]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceAnchor]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_anchor_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                **kwargs: Any
            ) -> ResourceAnchor: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ResourceAnchor]: ...


    class azure.mgmt.oracledatabase.aio.operations.SystemVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                systemversionname: str, 
                **kwargs: Any
            ) -> SystemVersion: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SystemVersion]: ...


    class azure.mgmt.oracledatabase.aio.operations.VirtualNetworkAddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                resource: VirtualNetworkAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkAddress]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkAddress]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualNetworkAddress]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                **kwargs: Any
            ) -> VirtualNetworkAddress: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualNetworkAddress]: ...


namespace azure.mgmt.oracledatabase.models

    class azure.mgmt.oracledatabase.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.oracledatabase.models.ActivationLinks(_Model):
        existing_cloud_account_activation_link: Optional[str]
        new_cloud_account_activation_link: Optional[str]


    class azure.mgmt.oracledatabase.models.AddRemoveDbNode(_Model):
        db_servers: list[str]

        @overload
        def __init__(
                self, 
                *, 
                db_servers: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AddSubscriptionOperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.AllConnectionStringType(_Model):
        high: Optional[str]
        low: Optional[str]
        medium: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                high: Optional[str] = ..., 
                low: Optional[str] = ..., 
                medium: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ApexDetailsType(_Model):
        apex_version: Optional[str]
        ords_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apex_version: Optional[str] = ..., 
                ords_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabase(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AutonomousDatabaseBaseProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AutonomousDatabaseBaseProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseBackup(ProxyResource):
        id: str
        name: str
        properties: Optional[AutonomousDatabaseBackupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutonomousDatabaseBackupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseBackupLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseBackupProperties(_Model):
        autonomous_database_ocid: Optional[str]
        backup_type: Optional[Union[str, AutonomousDatabaseBackupType]]
        database_size_in_tbs: Optional[float]
        db_version: Optional[str]
        display_name: Optional[str]
        is_automatic: Optional[bool]
        is_restorable: Optional[bool]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, AutonomousDatabaseBackupLifecycleState]]
        ocid: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        retention_period_in_days: Optional[int]
        size_in_tbs: Optional[float]
        time_available_til: Optional[datetime]
        time_ended: Optional[str]
        time_started: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                retention_period_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseBackupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        INCREMENTAL = "Incremental"
        LONG_TERM = "LongTerm"


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseBackupUpdate(_Model):
        properties: Optional[AutonomousDatabaseBackupUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutonomousDatabaseBackupUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseBackupUpdateProperties(_Model):
        retention_period_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                retention_period_in_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseBaseProperties(_Model):
        actual_used_data_storage_size_in_tbs: Optional[float]
        admin_password: Optional[str]
        allocated_storage_size_in_tbs: Optional[float]
        apex_details: Optional[ApexDetailsType]
        autonomous_database_id: Optional[str]
        autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]]
        available_upgrade_versions: Optional[list[str]]
        backup_retention_period_in_days: Optional[int]
        character_set: Optional[str]
        compute_count: Optional[float]
        compute_model: Optional[Union[str, ComputeModel]]
        connection_strings: Optional[ConnectionStringType]
        connection_urls: Optional[ConnectionUrlType]
        cpu_core_count: Optional[int]
        customer_contacts: Optional[list[CustomerContact]]
        data_base_type: str
        data_safe_status: Optional[Union[str, DataSafeStatusType]]
        data_storage_size_in_gbs: Optional[int]
        data_storage_size_in_tbs: Optional[int]
        database_edition: Optional[Union[str, DatabaseEditionType]]
        db_version: Optional[str]
        db_workload: Optional[Union[str, WorkloadType]]
        display_name: Optional[str]
        failed_data_recovery_in_seconds: Optional[int]
        in_memory_area_in_gbs: Optional[int]
        is_auto_scaling_enabled: Optional[bool]
        is_auto_scaling_for_storage_enabled: Optional[bool]
        is_local_data_guard_enabled: Optional[bool]
        is_mtls_connection_required: Optional[bool]
        is_preview: Optional[bool]
        is_preview_version_with_service_terms_accepted: Optional[bool]
        is_remote_data_guard_enabled: Optional[bool]
        license_model: Optional[Union[str, LicenseModel]]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, AutonomousDatabaseLifecycleState]]
        local_adg_auto_failover_max_data_loss_limit: Optional[int]
        local_disaster_recovery_type: Optional[Union[str, DisasterRecoveryType]]
        local_standby_db: Optional[AutonomousDatabaseStandbySummary]
        long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails]
        memory_per_oracle_compute_unit_in_gbs: Optional[int]
        ncharacter_set: Optional[str]
        next_long_term_backup_time_stamp: Optional[datetime]
        oci_url: Optional[str]
        ocid: Optional[str]
        open_mode: Optional[Union[str, OpenModeType]]
        operations_insights_status: Optional[Union[str, OperationsInsightsStatusType]]
        peer_db_id: Optional[str]
        peer_db_ids: Optional[list[str]]
        permission_level: Optional[Union[str, PermissionLevelType]]
        private_endpoint: Optional[str]
        private_endpoint_ip: Optional[str]
        private_endpoint_label: Optional[str]
        provisionable_cpus: Optional[list[int]]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        remote_disaster_recovery_configuration: Optional[DisasterRecoveryConfigurationDetails]
        role: Optional[Union[str, RoleType]]
        scheduled_operations_list: Optional[list[ScheduledOperationsType]]
        service_console_url: Optional[str]
        sql_web_developer_url: Optional[str]
        subnet_id: Optional[str]
        supported_regions_to_clone_to: Optional[list[str]]
        time_created: Optional[datetime]
        time_data_guard_role_changed: Optional[str]
        time_deletion_of_free_autonomous_database: Optional[str]
        time_disaster_recovery_role_changed: Optional[datetime]
        time_local_data_guard_enabled: Optional[str]
        time_maintenance_begin: Optional[datetime]
        time_maintenance_end: Optional[datetime]
        time_of_last_failover: Optional[str]
        time_of_last_refresh: Optional[str]
        time_of_last_refresh_point: Optional[str]
        time_of_last_switchover: Optional[str]
        time_reclamation_of_free_autonomous_database: Optional[str]
        used_data_storage_size_in_gbs: Optional[int]
        used_data_storage_size_in_tbs: Optional[int]
        vnet_id: Optional[str]
        whitelisted_ips: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                autonomous_database_id: Optional[str] = ..., 
                autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]] = ..., 
                backup_retention_period_in_days: Optional[int] = ..., 
                character_set: Optional[str] = ..., 
                compute_count: Optional[float] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                cpu_core_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                data_base_type: str, 
                data_storage_size_in_gbs: Optional[int] = ..., 
                data_storage_size_in_tbs: Optional[int] = ..., 
                database_edition: Optional[Union[str, DatabaseEditionType]] = ..., 
                db_version: Optional[str] = ..., 
                db_workload: Optional[Union[str, WorkloadType]] = ..., 
                display_name: Optional[str] = ..., 
                is_auto_scaling_enabled: Optional[bool] = ..., 
                is_auto_scaling_for_storage_enabled: Optional[bool] = ..., 
                is_local_data_guard_enabled: Optional[bool] = ..., 
                is_mtls_connection_required: Optional[bool] = ..., 
                is_preview_version_with_service_terms_accepted: Optional[bool] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                local_adg_auto_failover_max_data_loss_limit: Optional[int] = ..., 
                long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails] = ..., 
                ncharacter_set: Optional[str] = ..., 
                open_mode: Optional[Union[str, OpenModeType]] = ..., 
                peer_db_id: Optional[str] = ..., 
                permission_level: Optional[Union[str, PermissionLevelType]] = ..., 
                private_endpoint_ip: Optional[str] = ..., 
                private_endpoint_label: Optional[str] = ..., 
                role: Optional[Union[str, RoleType]] = ..., 
                scheduled_operations_list: Optional[list[ScheduledOperationsType]] = ..., 
                subnet_id: Optional[str] = ..., 
                vnet_id: Optional[str] = ..., 
                whitelisted_ips: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseCharacterSet(ProxyResource):
        id: str
        name: str
        properties: Optional[AutonomousDatabaseCharacterSetProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutonomousDatabaseCharacterSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseCharacterSetProperties(_Model):
        character_set: str

        @overload
        def __init__(
                self, 
                *, 
                character_set: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseCloneProperties(AutonomousDatabaseBaseProperties, discriminator='Clone'):
        actual_used_data_storage_size_in_tbs: float
        admin_password: str
        allocated_storage_size_in_tbs: float
        apex_details: ApexDetailsType
        autonomous_database_id: str
        autonomous_maintenance_schedule_type: Union[str, AutonomousMaintenanceScheduleType]
        available_upgrade_versions: list[str]
        backup_retention_period_in_days: int
        character_set: str
        clone_type: Union[str, CloneType]
        compute_count: float
        compute_model: Union[str, ComputeModel]
        connection_strings: ConnectionStringType
        connection_urls: ConnectionUrlType
        cpu_core_count: int
        customer_contacts: list[CustomerContact]
        data_base_type: Literal[DataBaseType.CLONE]
        data_safe_status: Union[str, DataSafeStatusType]
        data_storage_size_in_gbs: int
        data_storage_size_in_tbs: int
        database_edition: Union[str, DatabaseEditionType]
        db_version: str
        db_workload: Union[str, WorkloadType]
        display_name: str
        failed_data_recovery_in_seconds: int
        in_memory_area_in_gbs: int
        is_auto_scaling_enabled: bool
        is_auto_scaling_for_storage_enabled: bool
        is_local_data_guard_enabled: bool
        is_mtls_connection_required: bool
        is_preview: bool
        is_preview_version_with_service_terms_accepted: bool
        is_reconnect_clone_enabled: Optional[bool]
        is_refreshable_clone: Optional[bool]
        is_remote_data_guard_enabled: bool
        license_model: Union[str, LicenseModel]
        lifecycle_details: str
        lifecycle_state: Union[str, AutonomousDatabaseLifecycleState]
        local_adg_auto_failover_max_data_loss_limit: int
        local_disaster_recovery_type: Union[str, DisasterRecoveryType]
        local_standby_db: AutonomousDatabaseStandbySummary
        long_term_backup_schedule: LongTermBackUpScheduleDetails
        memory_per_oracle_compute_unit_in_gbs: int
        ncharacter_set: str
        next_long_term_backup_time_stamp: datetime
        oci_url: str
        ocid: str
        open_mode: Union[str, OpenModeType]
        operations_insights_status: Union[str, OperationsInsightsStatusType]
        peer_db_id: str
        peer_db_ids: list[str]
        permission_level: Union[str, PermissionLevelType]
        private_endpoint: str
        private_endpoint_ip: str
        private_endpoint_label: str
        provisionable_cpus: list[int]
        provisioning_state: Union[str, AzureResourceProvisioningState]
        refreshable_model: Optional[Union[str, RefreshableModelType]]
        refreshable_status: Optional[Union[str, RefreshableStatusType]]
        remote_disaster_recovery_configuration: DisasterRecoveryConfigurationDetails
        role: Union[str, RoleType]
        scheduled_operations_list: list[ScheduledOperationsType]
        service_console_url: str
        source: Optional[Union[str, SourceType]]
        source_id: str
        sql_web_developer_url: str
        subnet_id: str
        supported_regions_to_clone_to: list[str]
        time_created: datetime
        time_data_guard_role_changed: str
        time_deletion_of_free_autonomous_database: str
        time_disaster_recovery_role_changed: datetime
        time_local_data_guard_enabled: str
        time_maintenance_begin: datetime
        time_maintenance_end: datetime
        time_of_last_failover: str
        time_of_last_refresh: str
        time_of_last_refresh_point: str
        time_of_last_switchover: str
        time_reclamation_of_free_autonomous_database: str
        time_until_reconnect_clone_enabled: Optional[str]
        used_data_storage_size_in_gbs: int
        used_data_storage_size_in_tbs: int
        vnet_id: str
        whitelisted_ips: list[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                autonomous_database_id: Optional[str] = ..., 
                autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]] = ..., 
                backup_retention_period_in_days: Optional[int] = ..., 
                character_set: Optional[str] = ..., 
                clone_type: Union[str, CloneType], 
                compute_count: Optional[float] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                cpu_core_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                data_storage_size_in_gbs: Optional[int] = ..., 
                data_storage_size_in_tbs: Optional[int] = ..., 
                database_edition: Optional[Union[str, DatabaseEditionType]] = ..., 
                db_version: Optional[str] = ..., 
                db_workload: Optional[Union[str, WorkloadType]] = ..., 
                display_name: Optional[str] = ..., 
                is_auto_scaling_enabled: Optional[bool] = ..., 
                is_auto_scaling_for_storage_enabled: Optional[bool] = ..., 
                is_local_data_guard_enabled: Optional[bool] = ..., 
                is_mtls_connection_required: Optional[bool] = ..., 
                is_preview_version_with_service_terms_accepted: Optional[bool] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                local_adg_auto_failover_max_data_loss_limit: Optional[int] = ..., 
                long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails] = ..., 
                ncharacter_set: Optional[str] = ..., 
                open_mode: Optional[Union[str, OpenModeType]] = ..., 
                peer_db_id: Optional[str] = ..., 
                permission_level: Optional[Union[str, PermissionLevelType]] = ..., 
                private_endpoint_ip: Optional[str] = ..., 
                private_endpoint_label: Optional[str] = ..., 
                refreshable_model: Optional[Union[str, RefreshableModelType]] = ..., 
                role: Optional[Union[str, RoleType]] = ..., 
                scheduled_operations_list: Optional[list[ScheduledOperationsType]] = ..., 
                source: Optional[Union[str, SourceType]] = ..., 
                source_id: str, 
                subnet_id: Optional[str] = ..., 
                time_until_reconnect_clone_enabled: Optional[str] = ..., 
                vnet_id: Optional[str] = ..., 
                whitelisted_ips: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseCrossRegionDisasterRecoveryProperties(AutonomousDatabaseBaseProperties, discriminator='CrossRegionDisasterRecovery'):
        actual_used_data_storage_size_in_tbs: float
        admin_password: str
        allocated_storage_size_in_tbs: float
        apex_details: ApexDetailsType
        autonomous_database_id: str
        autonomous_maintenance_schedule_type: Union[str, AutonomousMaintenanceScheduleType]
        available_upgrade_versions: list[str]
        backup_retention_period_in_days: int
        character_set: str
        compute_count: float
        compute_model: Union[str, ComputeModel]
        connection_strings: ConnectionStringType
        connection_urls: ConnectionUrlType
        cpu_core_count: int
        customer_contacts: list[CustomerContact]
        data_base_type: Literal[DataBaseType.CROSS_REGION_DISASTER_RECOVERY]
        data_safe_status: Union[str, DataSafeStatusType]
        data_storage_size_in_gbs: int
        data_storage_size_in_tbs: int
        database_edition: Union[str, DatabaseEditionType]
        db_version: str
        db_workload: Union[str, WorkloadType]
        display_name: str
        failed_data_recovery_in_seconds: int
        in_memory_area_in_gbs: int
        is_auto_scaling_enabled: bool
        is_auto_scaling_for_storage_enabled: bool
        is_local_data_guard_enabled: bool
        is_mtls_connection_required: bool
        is_preview: bool
        is_preview_version_with_service_terms_accepted: bool
        is_remote_data_guard_enabled: bool
        is_replicate_automatic_backups: Optional[bool]
        license_model: Union[str, LicenseModel]
        lifecycle_details: str
        lifecycle_state: Union[str, AutonomousDatabaseLifecycleState]
        local_adg_auto_failover_max_data_loss_limit: int
        local_disaster_recovery_type: Union[str, DisasterRecoveryType]
        local_standby_db: AutonomousDatabaseStandbySummary
        long_term_backup_schedule: LongTermBackUpScheduleDetails
        memory_per_oracle_compute_unit_in_gbs: int
        ncharacter_set: str
        next_long_term_backup_time_stamp: datetime
        oci_url: str
        ocid: str
        open_mode: Union[str, OpenModeType]
        operations_insights_status: Union[str, OperationsInsightsStatusType]
        peer_db_id: str
        peer_db_ids: list[str]
        permission_level: Union[str, PermissionLevelType]
        private_endpoint: str
        private_endpoint_ip: str
        private_endpoint_label: str
        provisionable_cpus: list[int]
        provisioning_state: Union[str, AzureResourceProvisioningState]
        remote_disaster_recovery_configuration: DisasterRecoveryConfigurationDetails
        remote_disaster_recovery_type: Union[str, DisasterRecoveryType]
        role: Union[str, RoleType]
        scheduled_operations_list: list[ScheduledOperationsType]
        service_console_url: str
        source: Literal[SourceType.CROSS_REGION_DISASTER_RECOVERY]
        source_id: str
        source_location: Optional[str]
        source_ocid: Optional[str]
        sql_web_developer_url: str
        subnet_id: str
        supported_regions_to_clone_to: list[str]
        time_created: datetime
        time_data_guard_role_changed: str
        time_deletion_of_free_autonomous_database: str
        time_disaster_recovery_role_changed: datetime
        time_local_data_guard_enabled: str
        time_maintenance_begin: datetime
        time_maintenance_end: datetime
        time_of_last_failover: str
        time_of_last_refresh: str
        time_of_last_refresh_point: str
        time_of_last_switchover: str
        time_reclamation_of_free_autonomous_database: str
        used_data_storage_size_in_gbs: int
        used_data_storage_size_in_tbs: int
        vnet_id: str
        whitelisted_ips: list[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                autonomous_database_id: Optional[str] = ..., 
                autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]] = ..., 
                backup_retention_period_in_days: Optional[int] = ..., 
                character_set: Optional[str] = ..., 
                compute_count: Optional[float] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                cpu_core_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                data_storage_size_in_gbs: Optional[int] = ..., 
                data_storage_size_in_tbs: Optional[int] = ..., 
                database_edition: Optional[Union[str, DatabaseEditionType]] = ..., 
                db_version: Optional[str] = ..., 
                db_workload: Optional[Union[str, WorkloadType]] = ..., 
                display_name: Optional[str] = ..., 
                is_auto_scaling_enabled: Optional[bool] = ..., 
                is_auto_scaling_for_storage_enabled: Optional[bool] = ..., 
                is_local_data_guard_enabled: Optional[bool] = ..., 
                is_mtls_connection_required: Optional[bool] = ..., 
                is_preview_version_with_service_terms_accepted: Optional[bool] = ..., 
                is_replicate_automatic_backups: Optional[bool] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                local_adg_auto_failover_max_data_loss_limit: Optional[int] = ..., 
                long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails] = ..., 
                ncharacter_set: Optional[str] = ..., 
                open_mode: Optional[Union[str, OpenModeType]] = ..., 
                peer_db_id: Optional[str] = ..., 
                permission_level: Optional[Union[str, PermissionLevelType]] = ..., 
                private_endpoint_ip: Optional[str] = ..., 
                private_endpoint_label: Optional[str] = ..., 
                remote_disaster_recovery_type: Union[str, DisasterRecoveryType], 
                role: Optional[Union[str, RoleType]] = ..., 
                scheduled_operations_list: Optional[list[ScheduledOperationsType]] = ..., 
                source: Literal[SourceType.CROSS_REGION_DISASTER_RECOVERY], 
                source_id: str, 
                source_location: Optional[str] = ..., 
                source_ocid: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                vnet_id: Optional[str] = ..., 
                whitelisted_ips: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseFromBackupTimestampProperties(AutonomousDatabaseBaseProperties, discriminator='CloneFromBackupTimestamp'):
        actual_used_data_storage_size_in_tbs: float
        admin_password: str
        allocated_storage_size_in_tbs: float
        apex_details: ApexDetailsType
        autonomous_database_id: str
        autonomous_maintenance_schedule_type: Union[str, AutonomousMaintenanceScheduleType]
        available_upgrade_versions: list[str]
        backup_retention_period_in_days: int
        character_set: str
        clone_type: Union[str, CloneType]
        compute_count: float
        compute_model: Union[str, ComputeModel]
        connection_strings: ConnectionStringType
        connection_urls: ConnectionUrlType
        cpu_core_count: int
        customer_contacts: list[CustomerContact]
        data_base_type: Literal[DataBaseType.CLONE_FROM_BACKUP_TIMESTAMP]
        data_safe_status: Union[str, DataSafeStatusType]
        data_storage_size_in_gbs: int
        data_storage_size_in_tbs: int
        database_edition: Union[str, DatabaseEditionType]
        db_version: str
        db_workload: Union[str, WorkloadType]
        display_name: str
        failed_data_recovery_in_seconds: int
        in_memory_area_in_gbs: int
        is_auto_scaling_enabled: bool
        is_auto_scaling_for_storage_enabled: bool
        is_local_data_guard_enabled: bool
        is_mtls_connection_required: bool
        is_preview: bool
        is_preview_version_with_service_terms_accepted: bool
        is_remote_data_guard_enabled: bool
        license_model: Union[str, LicenseModel]
        lifecycle_details: str
        lifecycle_state: Union[str, AutonomousDatabaseLifecycleState]
        local_adg_auto_failover_max_data_loss_limit: int
        local_disaster_recovery_type: Union[str, DisasterRecoveryType]
        local_standby_db: AutonomousDatabaseStandbySummary
        long_term_backup_schedule: LongTermBackUpScheduleDetails
        memory_per_oracle_compute_unit_in_gbs: int
        ncharacter_set: str
        next_long_term_backup_time_stamp: datetime
        oci_url: str
        ocid: str
        open_mode: Union[str, OpenModeType]
        operations_insights_status: Union[str, OperationsInsightsStatusType]
        peer_db_id: str
        peer_db_ids: list[str]
        permission_level: Union[str, PermissionLevelType]
        private_endpoint: str
        private_endpoint_ip: str
        private_endpoint_label: str
        provisionable_cpus: list[int]
        provisioning_state: Union[str, AzureResourceProvisioningState]
        remote_disaster_recovery_configuration: DisasterRecoveryConfigurationDetails
        role: Union[str, RoleType]
        scheduled_operations_list: list[ScheduledOperationsType]
        service_console_url: str
        source: Literal[SourceType.BACKUP_FROM_TIMESTAMP]
        source_id: str
        sql_web_developer_url: str
        subnet_id: str
        supported_regions_to_clone_to: list[str]
        time_created: datetime
        time_data_guard_role_changed: str
        time_deletion_of_free_autonomous_database: str
        time_disaster_recovery_role_changed: datetime
        time_local_data_guard_enabled: str
        time_maintenance_begin: datetime
        time_maintenance_end: datetime
        time_of_last_failover: str
        time_of_last_refresh: str
        time_of_last_refresh_point: str
        time_of_last_switchover: str
        time_reclamation_of_free_autonomous_database: str
        timestamp: Optional[datetime]
        use_latest_available_backup_time_stamp: Optional[bool]
        used_data_storage_size_in_gbs: int
        used_data_storage_size_in_tbs: int
        vnet_id: str
        whitelisted_ips: list[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                autonomous_database_id: Optional[str] = ..., 
                autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]] = ..., 
                backup_retention_period_in_days: Optional[int] = ..., 
                character_set: Optional[str] = ..., 
                clone_type: Union[str, CloneType], 
                compute_count: Optional[float] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                cpu_core_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                data_storage_size_in_gbs: Optional[int] = ..., 
                data_storage_size_in_tbs: Optional[int] = ..., 
                database_edition: Optional[Union[str, DatabaseEditionType]] = ..., 
                db_version: Optional[str] = ..., 
                db_workload: Optional[Union[str, WorkloadType]] = ..., 
                display_name: Optional[str] = ..., 
                is_auto_scaling_enabled: Optional[bool] = ..., 
                is_auto_scaling_for_storage_enabled: Optional[bool] = ..., 
                is_local_data_guard_enabled: Optional[bool] = ..., 
                is_mtls_connection_required: Optional[bool] = ..., 
                is_preview_version_with_service_terms_accepted: Optional[bool] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                local_adg_auto_failover_max_data_loss_limit: Optional[int] = ..., 
                long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails] = ..., 
                ncharacter_set: Optional[str] = ..., 
                open_mode: Optional[Union[str, OpenModeType]] = ..., 
                peer_db_id: Optional[str] = ..., 
                permission_level: Optional[Union[str, PermissionLevelType]] = ..., 
                private_endpoint_ip: Optional[str] = ..., 
                private_endpoint_label: Optional[str] = ..., 
                role: Optional[Union[str, RoleType]] = ..., 
                scheduled_operations_list: Optional[list[ScheduledOperationsType]] = ..., 
                source: Literal[SourceType.BACKUP_FROM_TIMESTAMP], 
                source_id: str, 
                subnet_id: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                use_latest_available_backup_time_stamp: Optional[bool] = ..., 
                vnet_id: Optional[str] = ..., 
                whitelisted_ips: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseLifecycleAction(_Model):
        action: Union[str, AutonomousDatabaseLifecycleActionEnum]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, AutonomousDatabaseLifecycleActionEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseLifecycleActionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESTART = "Restart"
        START = "Start"
        STOP = "Stop"


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        AVAILABLE_NEEDS_ATTENTION = "AvailableNeedsAttention"
        BACKUP_IN_PROGRESS = "BackupInProgress"
        INACCESSIBLE = "Inaccessible"
        MAINTENANCE_IN_PROGRESS = "MaintenanceInProgress"
        PROVISIONING = "Provisioning"
        RECREATING = "Recreating"
        RESTARTING = "Restarting"
        RESTORE_FAILED = "RestoreFailed"
        RESTORE_IN_PROGRESS = "RestoreInProgress"
        ROLE_CHANGE_IN_PROGRESS = "RoleChangeInProgress"
        SCALE_IN_PROGRESS = "ScaleInProgress"
        STANDBY = "Standby"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UNAVAILABLE = "Unavailable"
        UPDATING = "Updating"
        UPGRADING = "Upgrading"


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseNationalCharacterSet(ProxyResource):
        id: str
        name: str
        properties: Optional[AutonomousDatabaseNationalCharacterSetProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutonomousDatabaseNationalCharacterSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseNationalCharacterSetProperties(_Model):
        character_set: str

        @overload
        def __init__(
                self, 
                *, 
                character_set: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseProperties(AutonomousDatabaseBaseProperties, discriminator='Regular'):
        actual_used_data_storage_size_in_tbs: float
        admin_password: str
        allocated_storage_size_in_tbs: float
        apex_details: ApexDetailsType
        autonomous_database_id: str
        autonomous_maintenance_schedule_type: Union[str, AutonomousMaintenanceScheduleType]
        available_upgrade_versions: list[str]
        backup_retention_period_in_days: int
        character_set: str
        compute_count: float
        compute_model: Union[str, ComputeModel]
        connection_strings: ConnectionStringType
        connection_urls: ConnectionUrlType
        cpu_core_count: int
        customer_contacts: list[CustomerContact]
        data_base_type: Literal[DataBaseType.REGULAR]
        data_safe_status: Union[str, DataSafeStatusType]
        data_storage_size_in_gbs: int
        data_storage_size_in_tbs: int
        database_edition: Union[str, DatabaseEditionType]
        db_version: str
        db_workload: Union[str, WorkloadType]
        display_name: str
        failed_data_recovery_in_seconds: int
        in_memory_area_in_gbs: int
        is_auto_scaling_enabled: bool
        is_auto_scaling_for_storage_enabled: bool
        is_local_data_guard_enabled: bool
        is_mtls_connection_required: bool
        is_preview: bool
        is_preview_version_with_service_terms_accepted: bool
        is_remote_data_guard_enabled: bool
        license_model: Union[str, LicenseModel]
        lifecycle_details: str
        lifecycle_state: Union[str, AutonomousDatabaseLifecycleState]
        local_adg_auto_failover_max_data_loss_limit: int
        local_disaster_recovery_type: Union[str, DisasterRecoveryType]
        local_standby_db: AutonomousDatabaseStandbySummary
        long_term_backup_schedule: LongTermBackUpScheduleDetails
        memory_per_oracle_compute_unit_in_gbs: int
        ncharacter_set: str
        next_long_term_backup_time_stamp: datetime
        oci_url: str
        ocid: str
        open_mode: Union[str, OpenModeType]
        operations_insights_status: Union[str, OperationsInsightsStatusType]
        peer_db_id: str
        peer_db_ids: list[str]
        permission_level: Union[str, PermissionLevelType]
        private_endpoint: str
        private_endpoint_ip: str
        private_endpoint_label: str
        provisionable_cpus: list[int]
        provisioning_state: Union[str, AzureResourceProvisioningState]
        remote_disaster_recovery_configuration: DisasterRecoveryConfigurationDetails
        role: Union[str, RoleType]
        scheduled_operations_list: list[ScheduledOperationsType]
        service_console_url: str
        sql_web_developer_url: str
        subnet_id: str
        supported_regions_to_clone_to: list[str]
        time_created: datetime
        time_data_guard_role_changed: str
        time_deletion_of_free_autonomous_database: str
        time_disaster_recovery_role_changed: datetime
        time_local_data_guard_enabled: str
        time_maintenance_begin: datetime
        time_maintenance_end: datetime
        time_of_last_failover: str
        time_of_last_refresh: str
        time_of_last_refresh_point: str
        time_of_last_switchover: str
        time_reclamation_of_free_autonomous_database: str
        used_data_storage_size_in_gbs: int
        used_data_storage_size_in_tbs: int
        vnet_id: str
        whitelisted_ips: list[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                autonomous_database_id: Optional[str] = ..., 
                autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]] = ..., 
                backup_retention_period_in_days: Optional[int] = ..., 
                character_set: Optional[str] = ..., 
                compute_count: Optional[float] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                cpu_core_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                data_storage_size_in_gbs: Optional[int] = ..., 
                data_storage_size_in_tbs: Optional[int] = ..., 
                database_edition: Optional[Union[str, DatabaseEditionType]] = ..., 
                db_version: Optional[str] = ..., 
                db_workload: Optional[Union[str, WorkloadType]] = ..., 
                display_name: Optional[str] = ..., 
                is_auto_scaling_enabled: Optional[bool] = ..., 
                is_auto_scaling_for_storage_enabled: Optional[bool] = ..., 
                is_local_data_guard_enabled: Optional[bool] = ..., 
                is_mtls_connection_required: Optional[bool] = ..., 
                is_preview_version_with_service_terms_accepted: Optional[bool] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                local_adg_auto_failover_max_data_loss_limit: Optional[int] = ..., 
                long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails] = ..., 
                ncharacter_set: Optional[str] = ..., 
                open_mode: Optional[Union[str, OpenModeType]] = ..., 
                peer_db_id: Optional[str] = ..., 
                permission_level: Optional[Union[str, PermissionLevelType]] = ..., 
                private_endpoint_ip: Optional[str] = ..., 
                private_endpoint_label: Optional[str] = ..., 
                role: Optional[Union[str, RoleType]] = ..., 
                scheduled_operations_list: Optional[list[ScheduledOperationsType]] = ..., 
                subnet_id: Optional[str] = ..., 
                vnet_id: Optional[str] = ..., 
                whitelisted_ips: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseStandbySummary(_Model):
        lag_time_in_seconds: Optional[int]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, AutonomousDatabaseLifecycleState]]
        time_data_guard_role_changed: Optional[str]
        time_disaster_recovery_role_changed: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                lag_time_in_seconds: Optional[int] = ..., 
                lifecycle_details: Optional[str] = ..., 
                lifecycle_state: Optional[Union[str, AutonomousDatabaseLifecycleState]] = ..., 
                time_data_guard_role_changed: Optional[str] = ..., 
                time_disaster_recovery_role_changed: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseUpdate(_Model):
        properties: Optional[AutonomousDatabaseUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutonomousDatabaseUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseUpdateProperties(_Model):
        admin_password: Optional[str]
        autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]]
        backup_retention_period_in_days: Optional[int]
        compute_count: Optional[float]
        cpu_core_count: Optional[int]
        customer_contacts: Optional[list[CustomerContact]]
        data_storage_size_in_gbs: Optional[int]
        data_storage_size_in_tbs: Optional[int]
        database_edition: Optional[Union[str, DatabaseEditionType]]
        display_name: Optional[str]
        is_auto_scaling_enabled: Optional[bool]
        is_auto_scaling_for_storage_enabled: Optional[bool]
        is_local_data_guard_enabled: Optional[bool]
        is_mtls_connection_required: Optional[bool]
        license_model: Optional[Union[str, LicenseModel]]
        local_adg_auto_failover_max_data_loss_limit: Optional[int]
        long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails]
        open_mode: Optional[Union[str, OpenModeType]]
        peer_db_id: Optional[str]
        permission_level: Optional[Union[str, PermissionLevelType]]
        role: Optional[Union[str, RoleType]]
        scheduled_operations_list: Optional[list[ScheduledOperationsTypeUpdate]]
        whitelisted_ips: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                autonomous_maintenance_schedule_type: Optional[Union[str, AutonomousMaintenanceScheduleType]] = ..., 
                backup_retention_period_in_days: Optional[int] = ..., 
                compute_count: Optional[float] = ..., 
                cpu_core_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                data_storage_size_in_gbs: Optional[int] = ..., 
                data_storage_size_in_tbs: Optional[int] = ..., 
                database_edition: Optional[Union[str, DatabaseEditionType]] = ..., 
                display_name: Optional[str] = ..., 
                is_auto_scaling_enabled: Optional[bool] = ..., 
                is_auto_scaling_for_storage_enabled: Optional[bool] = ..., 
                is_local_data_guard_enabled: Optional[bool] = ..., 
                is_mtls_connection_required: Optional[bool] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                local_adg_auto_failover_max_data_loss_limit: Optional[int] = ..., 
                long_term_backup_schedule: Optional[LongTermBackUpScheduleDetails] = ..., 
                open_mode: Optional[Union[str, OpenModeType]] = ..., 
                peer_db_id: Optional[str] = ..., 
                permission_level: Optional[Union[str, PermissionLevelType]] = ..., 
                role: Optional[Union[str, RoleType]] = ..., 
                scheduled_operations_list: Optional[list[ScheduledOperationsTypeUpdate]] = ..., 
                whitelisted_ips: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDatabaseWalletFile(_Model):
        wallet_files: str

        @overload
        def __init__(
                self, 
                *, 
                wallet_files: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDbVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[AutonomousDbVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutonomousDbVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousDbVersionProperties(_Model):
        db_workload: Optional[Union[str, WorkloadType]]
        is_default_for_free: Optional[bool]
        is_default_for_paid: Optional[bool]
        is_free_tier_enabled: Optional[bool]
        is_paid_enabled: Optional[bool]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                db_workload: Optional[Union[str, WorkloadType]] = ..., 
                is_default_for_free: Optional[bool] = ..., 
                is_default_for_paid: Optional[bool] = ..., 
                is_free_tier_enabled: Optional[bool] = ..., 
                is_paid_enabled: Optional[bool] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.AutonomousMaintenanceScheduleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EARLY = "Early"
        REGULAR = "Regular"


    class azure.mgmt.oracledatabase.models.AzureResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.oracledatabase.models.AzureSubscriptions(_Model):
        azure_subscription_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_subscription_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.BaseDbSystemShapes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM_STANDARD_X86 = "VM.Standard.x86"


    class azure.mgmt.oracledatabase.models.CloneType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        METADATA = "Metadata"


    class azure.mgmt.oracledatabase.models.CloudAccountDetails(_Model):
        cloud_account_home_region: Optional[str]
        cloud_account_name: Optional[str]


    class azure.mgmt.oracledatabase.models.CloudAccountProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        PENDING = "Pending"
        PROVISIONING = "Provisioning"


    class azure.mgmt.oracledatabase.models.CloudExadataInfrastructure(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CloudExadataInfrastructureProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CloudExadataInfrastructureProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.CloudExadataInfrastructureLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        FAILED = "Failed"
        MAINTENANCE_IN_PROGRESS = "MaintenanceInProgress"
        PROVISIONING = "Provisioning"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.CloudExadataInfrastructureProperties(_Model):
        activated_storage_count: Optional[int]
        additional_storage_count: Optional[int]
        available_storage_size_in_gbs: Optional[int]
        compute_count: Optional[int]
        compute_model: Optional[Union[str, ComputeModel]]
        cpu_count: Optional[int]
        customer_contacts: Optional[list[CustomerContact]]
        data_storage_size_in_tbs: Optional[float]
        database_server_type: Optional[str]
        db_node_storage_size_in_gbs: Optional[int]
        db_server_version: Optional[str]
        defined_file_system_configuration: Optional[list[DefinedFileSystemConfiguration]]
        display_name: str
        estimated_patching_time: Optional[EstimatedPatchingTime]
        exascale_config: Optional[ExascaleConfigDetails]
        last_maintenance_run_id: Optional[str]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, CloudExadataInfrastructureLifecycleState]]
        maintenance_window: Optional[MaintenanceWindow]
        max_cpu_count: Optional[int]
        max_data_storage_in_tbs: Optional[float]
        max_db_node_storage_size_in_gbs: Optional[int]
        max_memory_in_gbs: Optional[int]
        memory_size_in_gbs: Optional[int]
        monthly_db_server_version: Optional[str]
        monthly_storage_server_version: Optional[str]
        next_maintenance_run_id: Optional[str]
        oci_url: Optional[str]
        ocid: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        shape: str
        storage_count: Optional[int]
        storage_server_type: Optional[str]
        storage_server_version: Optional[str]
        time_created: Optional[str]
        total_storage_size_in_gbs: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                compute_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                database_server_type: Optional[str] = ..., 
                display_name: str, 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                shape: str, 
                storage_count: Optional[int] = ..., 
                storage_server_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.CloudExadataInfrastructureUpdate(_Model):
        properties: Optional[CloudExadataInfrastructureUpdateProperties]
        tags: Optional[dict[str, str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudExadataInfrastructureUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.CloudExadataInfrastructureUpdateProperties(_Model):
        compute_count: Optional[int]
        customer_contacts: Optional[list[CustomerContact]]
        display_name: Optional[str]
        maintenance_window: Optional[MaintenanceWindow]
        storage_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                compute_count: Optional[int] = ..., 
                customer_contacts: Optional[list[CustomerContact]] = ..., 
                display_name: Optional[str] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                storage_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.CloudVmCluster(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CloudVmClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CloudVmClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.CloudVmClusterLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        FAILED = "Failed"
        MAINTENANCE_IN_PROGRESS = "MaintenanceInProgress"
        PROVISIONING = "Provisioning"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.CloudVmClusterProperties(_Model):
        backup_subnet_cidr: Optional[str]
        cloud_exadata_infrastructure_id: str
        cluster_name: Optional[str]
        compartment_id: Optional[str]
        compute_model: Optional[Union[str, ComputeModel]]
        compute_nodes: Optional[list[str]]
        cpu_core_count: int
        data_collection_options: Optional[DataCollectionOptions]
        data_storage_percentage: Optional[int]
        data_storage_size_in_tbs: Optional[float]
        db_node_storage_size_in_gbs: Optional[int]
        db_servers: Optional[list[str]]
        disk_redundancy: Optional[Union[str, DiskRedundancy]]
        display_name: str
        domain: Optional[str]
        exascale_db_storage_vault_id: Optional[str]
        file_system_configuration_details: Optional[list[FileSystemConfigurationDetails]]
        gi_version: str
        hostname: str
        iorm_config_cache: Optional[ExadataIormConfig]
        is_local_backup_enabled: Optional[bool]
        is_sparse_diskgroup_enabled: Optional[bool]
        last_update_history_entry_id: Optional[str]
        license_model: Optional[Union[str, LicenseModel]]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, CloudVmClusterLifecycleState]]
        listener_port: Optional[int]
        memory_size_in_gbs: Optional[int]
        node_count: Optional[int]
        nsg_cidrs: Optional[list[NsgCidr]]
        nsg_url: Optional[str]
        oci_url: Optional[str]
        ocid: Optional[str]
        ocpu_count: Optional[float]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        scan_dns_name: Optional[str]
        scan_dns_record_id: Optional[str]
        scan_ip_ids: Optional[list[str]]
        scan_listener_port_tcp: Optional[int]
        scan_listener_port_tcp_ssl: Optional[int]
        shape: Optional[str]
        ssh_public_keys: list[str]
        storage_management_type: Optional[Union[str, ExadataVmClusterStorageManagementType]]
        storage_size_in_gbs: Optional[int]
        subnet_id: str
        subnet_ocid: Optional[str]
        system_version: Optional[str]
        time_created: Optional[datetime]
        time_zone: Optional[str]
        vip_ids: Optional[list[str]]
        vnet_id: str
        zone_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_subnet_cidr: Optional[str] = ..., 
                cloud_exadata_infrastructure_id: str, 
                cluster_name: Optional[str] = ..., 
                compute_nodes: Optional[list[str]] = ..., 
                cpu_core_count: int, 
                data_collection_options: Optional[DataCollectionOptions] = ..., 
                data_storage_percentage: Optional[int] = ..., 
                data_storage_size_in_tbs: Optional[float] = ..., 
                db_node_storage_size_in_gbs: Optional[int] = ..., 
                db_servers: Optional[list[str]] = ..., 
                display_name: str, 
                domain: Optional[str] = ..., 
                exascale_db_storage_vault_id: Optional[str] = ..., 
                file_system_configuration_details: Optional[list[FileSystemConfigurationDetails]] = ..., 
                gi_version: str, 
                hostname: str, 
                is_local_backup_enabled: Optional[bool] = ..., 
                is_sparse_diskgroup_enabled: Optional[bool] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                memory_size_in_gbs: Optional[int] = ..., 
                nsg_cidrs: Optional[list[NsgCidr]] = ..., 
                ocpu_count: Optional[float] = ..., 
                scan_listener_port_tcp: Optional[int] = ..., 
                scan_listener_port_tcp_ssl: Optional[int] = ..., 
                ssh_public_keys: list[str], 
                storage_size_in_gbs: Optional[int] = ..., 
                subnet_id: str, 
                system_version: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                vnet_id: str, 
                zone_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.CloudVmClusterUpdate(_Model):
        properties: Optional[CloudVmClusterUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudVmClusterUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.CloudVmClusterUpdateProperties(_Model):
        compute_nodes: Optional[list[str]]
        cpu_core_count: Optional[int]
        data_collection_options: Optional[DataCollectionOptions]
        data_storage_size_in_tbs: Optional[float]
        db_node_storage_size_in_gbs: Optional[int]
        display_name: Optional[str]
        file_system_configuration_details: Optional[list[FileSystemConfigurationDetails]]
        license_model: Optional[Union[str, LicenseModel]]
        memory_size_in_gbs: Optional[int]
        ocpu_count: Optional[float]
        ssh_public_keys: Optional[list[str]]
        storage_size_in_gbs: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                compute_nodes: Optional[list[str]] = ..., 
                cpu_core_count: Optional[int] = ..., 
                data_collection_options: Optional[DataCollectionOptions] = ..., 
                data_storage_size_in_tbs: Optional[float] = ..., 
                db_node_storage_size_in_gbs: Optional[int] = ..., 
                display_name: Optional[str] = ..., 
                file_system_configuration_details: Optional[list[FileSystemConfigurationDetails]] = ..., 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                memory_size_in_gbs: Optional[int] = ..., 
                ocpu_count: Optional[float] = ..., 
                ssh_public_keys: Optional[list[str]] = ..., 
                storage_size_in_gbs: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ComputeModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ECPU = "ECPU"
        OCPU = "OCPU"


    class azure.mgmt.oracledatabase.models.ConfigureExascaleCloudExadataInfrastructureDetails(_Model):
        total_storage_in_gbs: int

        @overload
        def __init__(
                self, 
                *, 
                total_storage_in_gbs: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ConnectionStringType(_Model):
        all_connection_strings: Optional[AllConnectionStringType]
        dedicated: Optional[str]
        high: Optional[str]
        low: Optional[str]
        medium: Optional[str]
        profiles: Optional[list[ProfileType]]

        @overload
        def __init__(
                self, 
                *, 
                all_connection_strings: Optional[AllConnectionStringType] = ..., 
                dedicated: Optional[str] = ..., 
                high: Optional[str] = ..., 
                low: Optional[str] = ..., 
                medium: Optional[str] = ..., 
                profiles: Optional[list[ProfileType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ConnectionUrlType(_Model):
        apex_url: Optional[str]
        database_transforms_url: Optional[str]
        graph_studio_url: Optional[str]
        machine_learning_notebook_url: Optional[str]
        mongo_db_url: Optional[str]
        ords_url: Optional[str]
        sql_dev_web_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apex_url: Optional[str] = ..., 
                database_transforms_url: Optional[str] = ..., 
                graph_studio_url: Optional[str] = ..., 
                machine_learning_notebook_url: Optional[str] = ..., 
                mongo_db_url: Optional[str] = ..., 
                ords_url: Optional[str] = ..., 
                sql_dev_web_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ConsumerGroup(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        TP = "Tp"
        TPURGENT = "Tpurgent"


    class azure.mgmt.oracledatabase.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.oracledatabase.models.CustomerContact(_Model):
        email: str

        @overload
        def __init__(
                self, 
                *, 
                email: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DataBaseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLONE = "Clone"
        CLONE_FROM_BACKUP_TIMESTAMP = "CloneFromBackupTimestamp"
        CROSS_REGION_DISASTER_RECOVERY = "CrossRegionDisasterRecovery"
        REGULAR = "Regular"


    class azure.mgmt.oracledatabase.models.DataCollectionOptions(_Model):
        is_diagnostics_events_enabled: Optional[bool]
        is_health_monitoring_enabled: Optional[bool]
        is_incident_logs_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_diagnostics_events_enabled: Optional[bool] = ..., 
                is_health_monitoring_enabled: Optional[bool] = ..., 
                is_incident_logs_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DataSafeStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEREGISTERING = "Deregistering"
        FAILED = "Failed"
        NOT_REGISTERED = "NotRegistered"
        REGISTERED = "Registered"
        REGISTERING = "Registering"


    class azure.mgmt.oracledatabase.models.DatabaseEditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE_EDITION = "EnterpriseEdition"
        STANDARD_EDITION = "StandardEdition"


    class azure.mgmt.oracledatabase.models.DayOfWeek(_Model):
        name: Union[str, DayOfWeekName]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, DayOfWeekName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DayOfWeekName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.oracledatabase.models.DayOfWeekUpdate(_Model):
        name: Optional[Union[str, DayOfWeekName]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, DayOfWeekName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbActionResponse(_Model):
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, AzureResourceProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbIormConfig(_Model):
        db_name: Optional[str]
        flash_cache_limit: Optional[str]
        share: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                db_name: Optional[str] = ..., 
                flash_cache_limit: Optional[str] = ..., 
                share: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbNode(ProxyResource):
        id: str
        name: str
        properties: Optional[DbNodeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DbNodeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbNodeAction(_Model):
        action: Union[str, DbNodeActionEnum]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, DbNodeActionEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbNodeActionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESET = "Reset"
        SOFT_RESET = "SoftReset"
        START = "Start"
        STOP = "Stop"


    class azure.mgmt.oracledatabase.models.DbNodeDetails(_Model):
        db_node_id: str

        @overload
        def __init__(
                self, 
                *, 
                db_node_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbNodeMaintenanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VMDB_REBOOT_MIGRATION = "VmdbRebootMigration"


    class azure.mgmt.oracledatabase.models.DbNodeProperties(_Model):
        additional_details: Optional[str]
        backup_ip_id: Optional[str]
        backup_vnic2_id: Optional[str]
        backup_vnic_id: Optional[str]
        cpu_core_count: Optional[int]
        db_node_storage_size_in_gbs: Optional[int]
        db_server_id: Optional[str]
        db_system_id: str
        fault_domain: Optional[str]
        host_ip_id: Optional[str]
        hostname: Optional[str]
        lifecycle_details: Optional[str]
        lifecycle_state: Union[str, DbNodeProvisioningState]
        maintenance_type: Optional[Union[str, DbNodeMaintenanceType]]
        memory_size_in_gbs: Optional[int]
        ocid: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        software_storage_size_in_gb: Optional[int]
        time_created: datetime
        time_maintenance_window_end: Optional[datetime]
        time_maintenance_window_start: Optional[datetime]
        vnic2_id: Optional[str]
        vnic_id: str

        @overload
        def __init__(
                self, 
                *, 
                additional_details: Optional[str] = ..., 
                backup_ip_id: Optional[str] = ..., 
                backup_vnic2_id: Optional[str] = ..., 
                backup_vnic_id: Optional[str] = ..., 
                cpu_core_count: Optional[int] = ..., 
                db_node_storage_size_in_gbs: Optional[int] = ..., 
                db_server_id: Optional[str] = ..., 
                db_system_id: str, 
                fault_domain: Optional[str] = ..., 
                host_ip_id: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                lifecycle_details: Optional[str] = ..., 
                lifecycle_state: Union[str, DbNodeProvisioningState], 
                maintenance_type: Optional[Union[str, DbNodeMaintenanceType]] = ..., 
                memory_size_in_gbs: Optional[int] = ..., 
                ocid: str, 
                software_storage_size_in_gb: Optional[int] = ..., 
                time_created: datetime, 
                time_maintenance_window_end: Optional[datetime] = ..., 
                time_maintenance_window_start: Optional[datetime] = ..., 
                vnic2_id: Optional[str] = ..., 
                vnic_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbNodeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.DbServer(ProxyResource):
        id: str
        name: str
        properties: Optional[DbServerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DbServerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbServerPatchingDetails(_Model):
        estimated_patch_duration: Optional[int]
        patching_status: Optional[Union[str, DbServerPatchingStatus]]
        time_patching_ended: Optional[datetime]
        time_patching_started: Optional[datetime]


    class azure.mgmt.oracledatabase.models.DbServerPatchingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        FAILED = "Failed"
        MAINTENANCE_IN_PROGRESS = "MaintenanceInProgress"
        SCHEDULED = "Scheduled"


    class azure.mgmt.oracledatabase.models.DbServerProperties(_Model):
        autonomous_virtual_machine_ids: Optional[list[str]]
        autonomous_vm_cluster_ids: Optional[list[str]]
        compartment_id: Optional[str]
        compute_model: Optional[Union[str, ComputeModel]]
        cpu_core_count: Optional[int]
        db_node_ids: Optional[list[str]]
        db_node_storage_size_in_gbs: Optional[int]
        db_server_patching_details: Optional[DbServerPatchingDetails]
        display_name: Optional[str]
        exadata_infrastructure_id: Optional[str]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, DbServerProvisioningState]]
        max_cpu_count: Optional[int]
        max_db_node_storage_in_gbs: Optional[int]
        max_memory_in_gbs: Optional[int]
        memory_size_in_gbs: Optional[int]
        ocid: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        shape: Optional[str]
        time_created: Optional[datetime]
        vm_cluster_ids: Optional[list[str]]


    class azure.mgmt.oracledatabase.models.DbServerProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        MAINTENANCE_IN_PROGRESS = "MaintenanceInProgress"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.oracledatabase.models.DbSystem(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DbSystemProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DbSystemProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbSystemBaseProperties(_Model):
        cluster_name: Optional[str]
        compute_count: Optional[int]
        compute_model: Optional[Union[str, ComputeModel]]
        data_storage_size_in_gbs: Optional[int]
        db_system_options: Optional[DbSystemOptions]
        disk_redundancy: Optional[Union[str, DiskRedundancyType]]
        display_name: Optional[str]
        domain_v2: Optional[str]
        grid_image_ocid: Optional[str]
        hostname: str
        initial_data_storage_size_in_gb: Optional[int]
        license_model_v2: Optional[Union[str, LicenseModel]]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, DbSystemLifecycleState]]
        listener_port: Optional[int]
        memory_size_in_gbs: Optional[int]
        network_anchor_id: str
        node_count: Optional[int]
        oci_url: Optional[str]
        ocid: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        resource_anchor_id: str
        scan_dns_name: Optional[str]
        scan_ips: Optional[list[str]]
        shape: str
        source: str
        ssh_public_keys: list[str]
        storage_volume_performance_mode: Optional[Union[str, StorageVolumePerformanceMode]]
        time_zone: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_name: Optional[str] = ..., 
                compute_count: Optional[int] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                db_system_options: Optional[DbSystemOptions] = ..., 
                disk_redundancy: Optional[Union[str, DiskRedundancyType]] = ..., 
                display_name: Optional[str] = ..., 
                domain_v2: Optional[str] = ..., 
                hostname: str, 
                initial_data_storage_size_in_gb: Optional[int] = ..., 
                license_model_v2: Optional[Union[str, LicenseModel]] = ..., 
                network_anchor_id: str, 
                node_count: Optional[int] = ..., 
                resource_anchor_id: str, 
                shape: str, 
                source: str = ..., 
                ssh_public_keys: list[str], 
                storage_volume_performance_mode: Optional[Union[str, StorageVolumePerformanceMode]] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbSystemDatabaseEditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE_EDITION = "EnterpriseEdition"
        ENTERPRISE_EDITION_DEVELOPER = "EnterpriseEditionDeveloper"
        ENTERPRISE_EDITION_EXTREME = "EnterpriseEditionExtreme"
        ENTERPRISE_EDITION_HIGH_PERFORMANCE = "EnterpriseEditionHighPerformance"
        STANDARD_EDITION = "StandardEdition"


    class azure.mgmt.oracledatabase.models.DbSystemLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        FAILED = "Failed"
        MAINTENANCE_IN_PROGRESS = "MaintenanceInProgress"
        MIGRATED = "Migrated"
        NEEDS_ATTENTION = "NeedsAttention"
        PROVISIONING = "Provisioning"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UPDATING = "Updating"
        UPGRADING = "Upgrading"


    class azure.mgmt.oracledatabase.models.DbSystemOptions(_Model):
        storage_management: Optional[Union[str, StorageManagementType]]

        @overload
        def __init__(
                self, 
                *, 
                storage_management: Optional[Union[str, StorageManagementType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbSystemProperties(DbSystemBaseProperties, discriminator='None'):
        admin_password: Optional[str]
        cluster_name: str
        compute_count: int
        compute_model: Union[str, ComputeModel]
        data_storage_size_in_gbs: int
        database_edition: Union[str, DbSystemDatabaseEditionType]
        db_system_options: DbSystemOptions
        db_version: str
        disk_redundancy: Union[str, DiskRedundancyType]
        display_name: str
        domain_v2: str
        grid_image_ocid: str
        hostname: str
        initial_data_storage_size_in_gb: int
        license_model_v2: Union[str, LicenseModel]
        lifecycle_details: str
        lifecycle_state: Union[str, DbSystemLifecycleState]
        listener_port: int
        memory_size_in_gbs: int
        network_anchor_id: str
        node_count: int
        oci_url: str
        ocid: str
        pdb_name: Optional[str]
        provisioning_state: Union[str, AzureResourceProvisioningState]
        resource_anchor_id: str
        scan_dns_name: str
        scan_ips: list[str]
        shape: str
        source: Literal[DbSystemSourceType.NONE]
        ssh_public_keys: list[str]
        storage_volume_performance_mode: Union[str, StorageVolumePerformanceMode]
        time_zone: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                cluster_name: Optional[str] = ..., 
                compute_count: Optional[int] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                database_edition: Union[str, DbSystemDatabaseEditionType], 
                db_system_options: Optional[DbSystemOptions] = ..., 
                db_version: str, 
                disk_redundancy: Optional[Union[str, DiskRedundancyType]] = ..., 
                display_name: Optional[str] = ..., 
                domain_v2: Optional[str] = ..., 
                hostname: str, 
                initial_data_storage_size_in_gb: Optional[int] = ..., 
                license_model_v2: Optional[Union[str, LicenseModel]] = ..., 
                network_anchor_id: str, 
                node_count: Optional[int] = ..., 
                pdb_name: Optional[str] = ..., 
                resource_anchor_id: str, 
                shape: str, 
                ssh_public_keys: list[str], 
                storage_volume_performance_mode: Optional[Union[str, StorageVolumePerformanceMode]] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbSystemShape(ProxyResource):
        id: str
        name: str
        properties: Optional[DbSystemShapeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DbSystemShapeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbSystemShapeProperties(_Model):
        are_server_types_supported: Optional[bool]
        available_core_count: int
        available_core_count_per_node: Optional[int]
        available_data_storage_in_tbs: Optional[int]
        available_data_storage_per_server_in_tbs: Optional[float]
        available_db_node_per_node_in_gbs: Optional[int]
        available_db_node_storage_in_gbs: Optional[int]
        available_memory_in_gbs: Optional[int]
        available_memory_per_node_in_gbs: Optional[int]
        compute_model: Optional[Union[str, ComputeModel]]
        core_count_increment: Optional[int]
        display_name: Optional[str]
        max_storage_count: Optional[int]
        maximum_node_count: Optional[int]
        min_core_count_per_node: Optional[int]
        min_data_storage_in_tbs: Optional[int]
        min_db_node_storage_per_node_in_gbs: Optional[int]
        min_memory_per_node_in_gbs: Optional[int]
        min_storage_count: Optional[int]
        minimum_core_count: Optional[int]
        minimum_node_count: Optional[int]
        runtime_minimum_core_count: Optional[int]
        shape_attributes: Optional[list[str]]
        shape_family: Optional[str]
        shape_name: str

        @overload
        def __init__(
                self, 
                *, 
                are_server_types_supported: Optional[bool] = ..., 
                available_core_count: int, 
                available_core_count_per_node: Optional[int] = ..., 
                available_data_storage_in_tbs: Optional[int] = ..., 
                available_data_storage_per_server_in_tbs: Optional[float] = ..., 
                available_db_node_per_node_in_gbs: Optional[int] = ..., 
                available_db_node_storage_in_gbs: Optional[int] = ..., 
                available_memory_in_gbs: Optional[int] = ..., 
                available_memory_per_node_in_gbs: Optional[int] = ..., 
                compute_model: Optional[Union[str, ComputeModel]] = ..., 
                core_count_increment: Optional[int] = ..., 
                display_name: Optional[str] = ..., 
                max_storage_count: Optional[int] = ..., 
                maximum_node_count: Optional[int] = ..., 
                min_core_count_per_node: Optional[int] = ..., 
                min_data_storage_in_tbs: Optional[int] = ..., 
                min_db_node_storage_per_node_in_gbs: Optional[int] = ..., 
                min_memory_per_node_in_gbs: Optional[int] = ..., 
                min_storage_count: Optional[int] = ..., 
                minimum_core_count: Optional[int] = ..., 
                minimum_node_count: Optional[int] = ..., 
                runtime_minimum_core_count: Optional[int] = ..., 
                shape_attributes: Optional[list[str]] = ..., 
                shape_family: Optional[str] = ..., 
                shape_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbSystemSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"


    class azure.mgmt.oracledatabase.models.DbSystemUpdate(_Model):
        properties: Optional[DbSystemUpdateProperties]
        tags: Optional[dict[str, str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DbSystemUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbSystemUpdateProperties(_Model):
        source: Optional[Literal[DbSystemSourceType.NONE]]

        @overload
        def __init__(
                self, 
                *, 
                source: Optional[Literal[DbSystemSourceType.NONE]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[DbVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DbVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DbVersionProperties(_Model):
        is_latest_for_major_version: Optional[bool]
        is_preview_db_version: Optional[bool]
        is_upgrade_supported: Optional[bool]
        supports_pdb: Optional[bool]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                is_latest_for_major_version: Optional[bool] = ..., 
                is_preview_db_version: Optional[bool] = ..., 
                is_upgrade_supported: Optional[bool] = ..., 
                supports_pdb: Optional[bool] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DefinedFileSystemConfiguration(_Model):
        is_backup_partition: Optional[bool]
        is_resizable: Optional[bool]
        min_size_gb: Optional[int]
        mount_point: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_backup_partition: Optional[bool] = ..., 
                is_resizable: Optional[bool] = ..., 
                min_size_gb: Optional[int] = ..., 
                mount_point: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DisasterRecoveryConfigurationDetails(_Model):
        disaster_recovery_type: Optional[Union[str, DisasterRecoveryType]]
        is_replicate_automatic_backups: Optional[bool]
        is_snapshot_standby: Optional[bool]
        time_snapshot_standby_enabled_till: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                disaster_recovery_type: Optional[Union[str, DisasterRecoveryType]] = ..., 
                is_replicate_automatic_backups: Optional[bool] = ..., 
                is_snapshot_standby: Optional[bool] = ..., 
                time_snapshot_standby_enabled_till: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DisasterRecoveryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADG = "Adg"
        BACKUP_BASED = "BackupBased"


    class azure.mgmt.oracledatabase.models.DiskRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        NORMAL = "Normal"


    class azure.mgmt.oracledatabase.models.DiskRedundancyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        NORMAL = "Normal"


    class azure.mgmt.oracledatabase.models.DnsForwardingRule(_Model):
        domain_names: str
        forwarding_ip_address: str

        @overload
        def __init__(
                self, 
                *, 
                domain_names: str, 
                forwarding_ip_address: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DnsPrivateView(ProxyResource):
        id: str
        name: str
        properties: Optional[DnsPrivateViewProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DnsPrivateViewProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DnsPrivateViewProperties(_Model):
        display_name: str
        is_protected: bool
        lifecycle_state: Union[str, DnsPrivateViewsLifecycleState]
        ocid: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        self_property: str
        time_created: datetime
        time_updated: datetime

        @overload
        def __init__(
                self, 
                *, 
                display_name: str, 
                is_protected: bool, 
                lifecycle_state: Union[str, DnsPrivateViewsLifecycleState], 
                ocid: str, 
                self_property: str, 
                time_created: datetime, 
                time_updated: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DnsPrivateViewsLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETED = "Deleted"
        DELETING = "Deleting"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.DnsPrivateZone(ProxyResource):
        id: str
        name: str
        properties: Optional[DnsPrivateZoneProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DnsPrivateZoneProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DnsPrivateZoneProperties(_Model):
        is_protected: bool
        lifecycle_state: Union[str, DnsPrivateZonesLifecycleState]
        ocid: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        self_property: str
        serial: int
        time_created: datetime
        version: str
        view_id: Optional[str]
        zone_type: Union[str, ZoneType]

        @overload
        def __init__(
                self, 
                *, 
                is_protected: bool, 
                lifecycle_state: Union[str, DnsPrivateZonesLifecycleState], 
                ocid: str, 
                self_property: str, 
                serial: int, 
                time_created: datetime, 
                version: str, 
                view_id: Optional[str] = ..., 
                zone_type: Union[str, ZoneType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.DnsPrivateZonesLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.oracledatabase.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.oracledatabase.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.EstimatedPatchingTime(_Model):
        estimated_db_server_patching_time: Optional[int]
        estimated_network_switches_patching_time: Optional[int]
        estimated_storage_server_patching_time: Optional[int]
        total_estimated_patching_time: Optional[int]


    class azure.mgmt.oracledatabase.models.ExadataIormConfig(_Model):
        db_plans: Optional[list[DbIormConfig]]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, IormLifecycleState]]
        objective: Optional[Union[str, Objective]]

        @overload
        def __init__(
                self, 
                *, 
                db_plans: Optional[list[DbIormConfig]] = ..., 
                lifecycle_details: Optional[str] = ..., 
                lifecycle_state: Optional[Union[str, IormLifecycleState]] = ..., 
                objective: Optional[Union[str, Objective]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExadataVmClusterStorageManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASM = "ASM"
        EXASCALE = "Exascale"


    class azure.mgmt.oracledatabase.models.ExadbVmCluster(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ExadbVmClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ExadbVmClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExadbVmClusterLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        FAILED = "Failed"
        MAINTENANCE_IN_PROGRESS = "MaintenanceInProgress"
        PROVISIONING = "Provisioning"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.ExadbVmClusterProperties(_Model):
        backup_subnet_cidr: Optional[str]
        backup_subnet_ocid: Optional[str]
        cluster_name: Optional[str]
        data_collection_options: Optional[DataCollectionOptions]
        display_name: str
        domain: Optional[str]
        enabled_ecpu_count: int
        exascale_db_storage_vault_id: str
        gi_version: Optional[str]
        grid_image_ocid: Optional[str]
        grid_image_type: Optional[Union[str, GridImageType]]
        hostname: str
        iorm_config_cache: Optional[ExadataIormConfig]
        license_model: Optional[Union[str, LicenseModel]]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, ExadbVmClusterLifecycleState]]
        listener_port: Optional[int]
        memory_size_in_gbs: Optional[int]
        node_count: int
        nsg_cidrs: Optional[list[NsgCidr]]
        nsg_url: Optional[str]
        oci_url: Optional[str]
        ocid: Optional[str]
        private_zone_ocid: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        scan_dns_name: Optional[str]
        scan_dns_record_id: Optional[str]
        scan_ip_ids: Optional[list[str]]
        scan_listener_port_tcp: Optional[int]
        scan_listener_port_tcp_ssl: Optional[int]
        shape: str
        shape_attribute: Optional[Union[str, ShapeAttribute]]
        snapshot_file_system_storage: Optional[ExadbVmClusterStorageDetails]
        ssh_public_keys: list[str]
        subnet_id: str
        subnet_ocid: Optional[str]
        system_version: Optional[str]
        time_zone: Optional[str]
        total_ecpu_count: int
        total_file_system_storage: Optional[ExadbVmClusterStorageDetails]
        vip_ids: Optional[list[str]]
        vm_file_system_storage: ExadbVmClusterStorageDetails
        vnet_id: str
        zone_ocid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_subnet_cidr: Optional[str] = ..., 
                cluster_name: Optional[str] = ..., 
                data_collection_options: Optional[DataCollectionOptions] = ..., 
                display_name: str, 
                domain: Optional[str] = ..., 
                enabled_ecpu_count: int, 
                exascale_db_storage_vault_id: str, 
                grid_image_ocid: Optional[str] = ..., 
                hostname: str, 
                license_model: Optional[Union[str, LicenseModel]] = ..., 
                node_count: int, 
                nsg_cidrs: Optional[list[NsgCidr]] = ..., 
                private_zone_ocid: Optional[str] = ..., 
                scan_listener_port_tcp: Optional[int] = ..., 
                scan_listener_port_tcp_ssl: Optional[int] = ..., 
                shape: str, 
                shape_attribute: Optional[Union[str, ShapeAttribute]] = ..., 
                ssh_public_keys: list[str], 
                subnet_id: str, 
                system_version: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                total_ecpu_count: int, 
                vm_file_system_storage: ExadbVmClusterStorageDetails, 
                vnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExadbVmClusterStorageDetails(_Model):
        total_size_in_gbs: int

        @overload
        def __init__(
                self, 
                *, 
                total_size_in_gbs: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExadbVmClusterUpdate(_Model):
        properties: Optional[ExadbVmClusterUpdateProperties]
        tags: Optional[dict[str, str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExadbVmClusterUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExadbVmClusterUpdateProperties(_Model):
        node_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                node_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleConfigDetails(_Model):
        available_storage_in_gbs: Optional[int]
        total_storage_in_gbs: int

        @overload
        def __init__(
                self, 
                *, 
                available_storage_in_gbs: Optional[int] = ..., 
                total_storage_in_gbs: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleDbNode(ProxyResource):
        id: str
        name: str
        properties: Optional[ExascaleDbNodeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExascaleDbNodeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleDbNodeProperties(_Model):
        additional_details: Optional[str]
        cpu_core_count: Optional[int]
        db_node_storage_size_in_gbs: Optional[int]
        fault_domain: Optional[str]
        hostname: Optional[str]
        lifecycle_state: Optional[Union[str, DbNodeProvisioningState]]
        maintenance_type: Optional[str]
        memory_size_in_gbs: Optional[int]
        ocid: str
        software_storage_size_in_gb: Optional[int]
        time_maintenance_window_end: Optional[datetime]
        time_maintenance_window_start: Optional[datetime]
        total_cpu_core_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                additional_details: Optional[str] = ..., 
                cpu_core_count: Optional[int] = ..., 
                db_node_storage_size_in_gbs: Optional[int] = ..., 
                fault_domain: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                lifecycle_state: Optional[Union[str, DbNodeProvisioningState]] = ..., 
                maintenance_type: Optional[str] = ..., 
                memory_size_in_gbs: Optional[int] = ..., 
                ocid: str, 
                software_storage_size_in_gb: Optional[int] = ..., 
                time_maintenance_window_end: Optional[datetime] = ..., 
                time_maintenance_window_start: Optional[datetime] = ..., 
                total_cpu_core_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleDbStorageDetails(_Model):
        available_size_in_gbs: Optional[int]
        total_size_in_gbs: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                available_size_in_gbs: Optional[int] = ..., 
                total_size_in_gbs: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleDbStorageInputDetails(_Model):
        total_size_in_gbs: int

        @overload
        def __init__(
                self, 
                *, 
                total_size_in_gbs: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleDbStorageVault(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ExascaleDbStorageVaultProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ExascaleDbStorageVaultProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleDbStorageVaultLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.ExascaleDbStorageVaultProperties(_Model):
        additional_flash_cache_in_percent: Optional[int]
        attached_shape_attributes: Optional[list[Union[str, ShapeAttribute]]]
        description: Optional[str]
        display_name: str
        exadata_infrastructure_id: Optional[str]
        high_capacity_database_storage: Optional[ExascaleDbStorageDetails]
        high_capacity_database_storage_input: ExascaleDbStorageInputDetails
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, ExascaleDbStorageVaultLifecycleState]]
        oci_url: Optional[str]
        ocid: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        time_zone: Optional[str]
        vm_cluster_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                additional_flash_cache_in_percent: Optional[int] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                exadata_infrastructure_id: Optional[str] = ..., 
                high_capacity_database_storage_input: ExascaleDbStorageInputDetails, 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ExascaleDbStorageVaultTagsUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.FileSystemConfigurationDetails(_Model):
        file_system_size_gb: Optional[int]
        mount_point: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_system_size_gb: Optional[int] = ..., 
                mount_point: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.FlexComponent(ProxyResource):
        id: str
        name: str
        properties: Optional[FlexComponentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FlexComponentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.FlexComponentProperties(_Model):
        available_core_count: Optional[int]
        available_db_storage_in_gbs: Optional[int]
        available_local_storage_in_gbs: Optional[int]
        available_memory_in_gbs: Optional[int]
        compute_model: Optional[str]
        description_summary: Optional[str]
        hardware_type: Optional[Union[str, HardwareType]]
        minimum_core_count: Optional[int]
        runtime_minimum_core_count: Optional[int]
        shape: Optional[str]


    class azure.mgmt.oracledatabase.models.GenerateAutonomousDatabaseWalletDetails(_Model):
        generate_type: Optional[Union[str, GenerateType]]
        is_regional: Optional[bool]
        password: str

        @overload
        def __init__(
                self, 
                *, 
                generate_type: Optional[Union[str, GenerateType]] = ..., 
                is_regional: Optional[bool] = ..., 
                password: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.GenerateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        SINGLE = "Single"


    class azure.mgmt.oracledatabase.models.GiMinorVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[GiMinorVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GiMinorVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.GiMinorVersionProperties(_Model):
        grid_image_ocid: Optional[str]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                grid_image_ocid: Optional[str] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.GiVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[GiVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GiVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.GiVersionProperties(_Model):
        version: str

        @overload
        def __init__(
                self, 
                *, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.GridImageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_IMAGE = "CustomImage"
        RELEASE_UPDATE = "ReleaseUpdate"


    class azure.mgmt.oracledatabase.models.HardwareType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CELL = "CELL"
        COMPUTE = "COMPUTE"


    class azure.mgmt.oracledatabase.models.HostFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDN = "Fqdn"
        IP = "Ip"


    class azure.mgmt.oracledatabase.models.Intent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESET = "Reset"
        RETAIN = "Retain"


    class azure.mgmt.oracledatabase.models.IormLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOT_STRAPPING = "BootStrapping"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        FAILED = "Failed"
        UPDATING = "Updating"


    class azure.mgmt.oracledatabase.models.LicenseModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BRING_YOUR_OWN_LICENSE = "BringYourOwnLicense"
        LICENSE_INCLUDED = "LicenseIncluded"


    class azure.mgmt.oracledatabase.models.LongTermBackUpScheduleDetails(_Model):
        is_disabled: Optional[bool]
        repeat_cadence: Optional[Union[str, RepeatCadenceType]]
        retention_period_in_days: Optional[int]
        time_of_backup: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                is_disabled: Optional[bool] = ..., 
                repeat_cadence: Optional[Union[str, RepeatCadenceType]] = ..., 
                retention_period_in_days: Optional[int] = ..., 
                time_of_backup: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.MaintenanceWindow(_Model):
        custom_action_timeout_in_mins: Optional[int]
        days_of_week: Optional[list[DayOfWeek]]
        hours_of_day: Optional[list[int]]
        is_custom_action_timeout_enabled: Optional[bool]
        is_monthly_patching_enabled: Optional[bool]
        lead_time_in_weeks: Optional[int]
        months: Optional[list[Month]]
        patching_mode: Optional[Union[str, PatchingMode]]
        preference: Optional[Union[str, Preference]]
        weeks_of_month: Optional[list[int]]

        @overload
        def __init__(
                self, 
                *, 
                custom_action_timeout_in_mins: Optional[int] = ..., 
                days_of_week: Optional[list[DayOfWeek]] = ..., 
                hours_of_day: Optional[list[int]] = ..., 
                is_custom_action_timeout_enabled: Optional[bool] = ..., 
                is_monthly_patching_enabled: Optional[bool] = ..., 
                lead_time_in_weeks: Optional[int] = ..., 
                months: Optional[list[Month]] = ..., 
                patching_mode: Optional[Union[str, PatchingMode]] = ..., 
                preference: Optional[Union[str, Preference]] = ..., 
                weeks_of_month: Optional[list[int]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.Month(_Model):
        name: Union[str, MonthName]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, MonthName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.MonthName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APRIL = "April"
        AUGUST = "August"
        DECEMBER = "December"
        FEBRUARY = "February"
        JANUARY = "January"
        JULY = "July"
        JUNE = "June"
        MARCH = "March"
        MAY = "May"
        NOVEMBER = "November"
        OCTOBER = "October"
        SEPTEMBER = "September"


    class azure.mgmt.oracledatabase.models.NetworkAnchor(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[NetworkAnchorProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NetworkAnchorProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.NetworkAnchorProperties(_Model):
        cidr_block: Optional[str]
        dns_forwarding_endpoint_ip_address: Optional[str]
        dns_forwarding_endpoint_nsg_rules_url: Optional[str]
        dns_forwarding_rules: Optional[list[DnsForwardingRule]]
        dns_forwarding_rules_url: Optional[str]
        dns_listening_endpoint_allowed_cidrs: Optional[str]
        dns_listening_endpoint_ip_address: Optional[str]
        dns_listening_endpoint_nsg_rules_url: Optional[str]
        is_oracle_dns_forwarding_endpoint_enabled: Optional[bool]
        is_oracle_dns_listening_endpoint_enabled: Optional[bool]
        is_oracle_to_azure_dns_zone_sync_enabled: Optional[bool]
        oci_backup_cidr_block: Optional[str]
        oci_subnet_id: Optional[str]
        oci_vcn_dns_label: Optional[str]
        oci_vcn_id: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        resource_anchor_id: str
        subnet_id: str
        vnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dns_forwarding_rules: Optional[list[DnsForwardingRule]] = ..., 
                dns_listening_endpoint_allowed_cidrs: Optional[str] = ..., 
                is_oracle_dns_forwarding_endpoint_enabled: Optional[bool] = ..., 
                is_oracle_dns_listening_endpoint_enabled: Optional[bool] = ..., 
                is_oracle_to_azure_dns_zone_sync_enabled: Optional[bool] = ..., 
                oci_backup_cidr_block: Optional[str] = ..., 
                oci_vcn_dns_label: Optional[str] = ..., 
                resource_anchor_id: str, 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.NetworkAnchorUpdate(_Model):
        properties: Optional[NetworkAnchorUpdateProperties]
        tags: Optional[dict[str, str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkAnchorUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.NetworkAnchorUpdateProperties(_Model):
        is_oracle_dns_forwarding_endpoint_enabled: Optional[bool]
        is_oracle_dns_listening_endpoint_enabled: Optional[bool]
        is_oracle_to_azure_dns_zone_sync_enabled: Optional[bool]
        oci_backup_cidr_block: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_oracle_dns_forwarding_endpoint_enabled: Optional[bool] = ..., 
                is_oracle_dns_listening_endpoint_enabled: Optional[bool] = ..., 
                is_oracle_to_azure_dns_zone_sync_enabled: Optional[bool] = ..., 
                oci_backup_cidr_block: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.NsgCidr(_Model):
        destination_port_range: Optional[PortRange]
        source: str

        @overload
        def __init__(
                self, 
                *, 
                destination_port_range: Optional[PortRange] = ..., 
                source: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.Objective(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        BALANCED = "Balanced"
        BASIC = "Basic"
        HIGH_THROUGHPUT = "HighThroughput"
        LOW_LATENCY = "LowLatency"


    class azure.mgmt.oracledatabase.models.OpenModeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.oracledatabase.models.Operation(_Model):
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


    class azure.mgmt.oracledatabase.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.oracledatabase.models.OperationsInsightsStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        FAILED_DISABLING = "FailedDisabling"
        FAILED_ENABLING = "FailedEnabling"
        NOT_ENABLED = "NotEnabled"


    class azure.mgmt.oracledatabase.models.OracleSubscription(ProxyResource):
        id: str
        name: str
        plan: Optional[Plan]
        properties: Optional[OracleSubscriptionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                plan: Optional[Plan] = ..., 
                properties: Optional[OracleSubscriptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.OracleSubscriptionProperties(_Model):
        add_subscription_operation_state: Optional[Union[str, AddSubscriptionOperationState]]
        azure_subscription_ids: Optional[list[str]]
        cloud_account_id: Optional[str]
        cloud_account_state: Optional[Union[str, CloudAccountProvisioningState]]
        intent: Optional[Union[str, Intent]]
        last_operation_status_detail: Optional[str]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, OracleSubscriptionProvisioningState]]
        saas_subscription_id: Optional[str]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                intent: Optional[Union[str, Intent]] = ..., 
                product_code: Optional[str] = ..., 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.OracleSubscriptionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.oracledatabase.models.OracleSubscriptionUpdate(_Model):
        plan: Optional[PlanUpdate]
        properties: Optional[OracleSubscriptionUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                plan: Optional[PlanUpdate] = ..., 
                properties: Optional[OracleSubscriptionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.OracleSubscriptionUpdateProperties(_Model):
        intent: Optional[Union[str, Intent]]
        product_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                intent: Optional[Union[str, Intent]] = ..., 
                product_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.oracledatabase.models.PatchingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_ROLLING = "NonRolling"
        ROLLING = "Rolling"


    class azure.mgmt.oracledatabase.models.PeerDbDetails(_Model):
        peer_db_id: Optional[str]
        peer_db_location: Optional[str]
        peer_db_ocid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                peer_db_id: Optional[str] = ..., 
                peer_db_location: Optional[str] = ..., 
                peer_db_ocid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.PermissionLevelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESTRICTED = "Restricted"
        UNRESTRICTED = "Unrestricted"


    class azure.mgmt.oracledatabase.models.Plan(_Model):
        name: str
        product: str
        promotion_code: Optional[str]
        publisher: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.PlanUpdate(_Model):
        name: Optional[str]
        product: Optional[str]
        promotion_code: Optional[str]
        publisher: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                product: Optional[str] = ..., 
                promotion_code: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.PortRange(_Model):
        max: int
        min: int

        @overload
        def __init__(
                self, 
                *, 
                max: int, 
                min: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.Preference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_PREFERENCE = "CustomPreference"
        NO_PREFERENCE = "NoPreference"


    class azure.mgmt.oracledatabase.models.PrivateIpAddressProperties(_Model):
        display_name: str
        hostname_label: str
        ip_address: str
        ocid: str
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                display_name: str, 
                hostname_label: str, 
                ip_address: str, 
                ocid: str, 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.PrivateIpAddressesFilter(_Model):
        subnet_id: str
        vnic_id: str

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: str, 
                vnic_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ProfileType(_Model):
        consumer_group: Optional[Union[str, ConsumerGroup]]
        display_name: str
        host_format: Union[str, HostFormatType]
        is_regional: Optional[bool]
        protocol: Union[str, ProtocolType]
        session_mode: Union[str, SessionModeType]
        syntax_format: Union[str, SyntaxFormatType]
        tls_authentication: Optional[Union[str, TlsAuthenticationType]]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                consumer_group: Optional[Union[str, ConsumerGroup]] = ..., 
                display_name: str, 
                host_format: Union[str, HostFormatType], 
                is_regional: Optional[bool] = ..., 
                protocol: Union[str, ProtocolType], 
                session_mode: Union[str, SessionModeType], 
                syntax_format: Union[str, SyntaxFormatType], 
                tls_authentication: Optional[Union[str, TlsAuthenticationType]] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        TCPS = "TCPS"


    class azure.mgmt.oracledatabase.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.oracledatabase.models.RefreshableModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.oracledatabase.models.RefreshableStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REFRESHING = "NotRefreshing"
        REFRESHING = "Refreshing"


    class azure.mgmt.oracledatabase.models.RemoveVirtualMachineFromExadbVmClusterDetails(_Model):
        db_nodes: list[DbNodeDetails]

        @overload
        def __init__(
                self, 
                *, 
                db_nodes: list[DbNodeDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.RepeatCadenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "Monthly"
        ONE_TIME = "OneTime"
        WEEKLY = "Weekly"
        YEARLY = "Yearly"


    class azure.mgmt.oracledatabase.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.oracledatabase.models.ResourceAnchor(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ResourceAnchorProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ResourceAnchorProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ResourceAnchorProperties(_Model):
        linked_compartment_id: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]


    class azure.mgmt.oracledatabase.models.ResourceAnchorUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.oracledatabase.models.RestoreAutonomousDatabaseDetails(_Model):
        timestamp: datetime

        @overload
        def __init__(
                self, 
                *, 
                timestamp: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.RoleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_COPY = "BackupCopy"
        DISABLED_STANDBY = "DisabledStandby"
        PRIMARY = "Primary"
        SNAPSHOT_STANDBY = "SnapshotStandby"
        STANDBY = "Standby"


    class azure.mgmt.oracledatabase.models.SaasSubscriptionDetails(_Model):
        id: Optional[str]
        is_auto_renew: Optional[bool]
        is_free_trial: Optional[bool]
        offer_id: Optional[str]
        plan_id: Optional[str]
        publisher_id: Optional[str]
        purchaser_email_id: Optional[str]
        purchaser_tenant_id: Optional[str]
        saas_subscription_status: Optional[str]
        subscription_name: Optional[str]
        term_unit: Optional[str]
        time_created: Optional[datetime]


    class azure.mgmt.oracledatabase.models.ScheduledOperationsType(_Model):
        day_of_week: DayOfWeek
        scheduled_start_time: Optional[str]
        scheduled_stop_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: DayOfWeek, 
                scheduled_start_time: Optional[str] = ..., 
                scheduled_stop_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.ScheduledOperationsTypeUpdate(_Model):
        day_of_week: Optional[DayOfWeekUpdate]
        scheduled_start_time: Optional[str]
        scheduled_stop_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: Optional[DayOfWeekUpdate] = ..., 
                scheduled_start_time: Optional[str] = ..., 
                scheduled_stop_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.SessionModeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        REDIRECT = "Redirect"


    class azure.mgmt.oracledatabase.models.ShapeAttribute(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK_STORAGE = "BLOCK_STORAGE"
        SMART_STORAGE = "SMART_STORAGE"


    class azure.mgmt.oracledatabase.models.ShapeFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXADATA = "EXADATA"
        EXADB_XS = "EXADB_XS"


    class azure.mgmt.oracledatabase.models.ShapeFamilyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXADATA = "EXADATA"
        EXADB_XS = "EXADB_XS"
        SINGLE_NODE = "SINGLENODE"
        VIRTUAL_MACHINE = "VIRTUALMACHINE"


    class azure.mgmt.oracledatabase.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_FROM_ID = "BackupFromId"
        BACKUP_FROM_TIMESTAMP = "BackupFromTimestamp"
        CLONE_TO_REFRESHABLE = "CloneToRefreshable"
        CROSS_REGION_DATAGUARD = "CrossRegionDataguard"
        CROSS_REGION_DISASTER_RECOVERY = "CrossRegionDisasterRecovery"
        DATABASE = "Database"
        NONE = "None"


    class azure.mgmt.oracledatabase.models.StorageManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LVM = "LVM"


    class azure.mgmt.oracledatabase.models.StorageVolumePerformanceMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BALANCED = "Balanced"
        HIGH_PERFORMANCE = "HighPerformance"


    class azure.mgmt.oracledatabase.models.SyntaxFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EZCONNECT = "Ezconnect"
        EZCONNECTPLUS = "Ezconnectplus"
        LONG = "Long"


    class azure.mgmt.oracledatabase.models.SystemData(_Model):
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


    class azure.mgmt.oracledatabase.models.SystemShapes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXADATA_X11_M = "Exadata.X11M"
        EXADATA_X9_M = "Exadata.X9M"
        EXA_DB_XS = "ExaDbXS"


    class azure.mgmt.oracledatabase.models.SystemVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[SystemVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SystemVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.SystemVersionProperties(_Model):
        system_version: str

        @overload
        def __init__(
                self, 
                *, 
                system_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.TlsAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MUTUAL = "Mutual"
        SERVER = "Server"


    class azure.mgmt.oracledatabase.models.TrackedResource(Resource):
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


    class azure.mgmt.oracledatabase.models.VirtualNetworkAddress(ProxyResource):
        id: str
        name: str
        properties: Optional[VirtualNetworkAddressProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualNetworkAddressProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.VirtualNetworkAddressLifecycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        TERMINATED = "Terminated"
        TERMINATING = "Terminating"


    class azure.mgmt.oracledatabase.models.VirtualNetworkAddressProperties(_Model):
        domain: Optional[str]
        ip_address: Optional[str]
        lifecycle_details: Optional[str]
        lifecycle_state: Optional[Union[str, VirtualNetworkAddressLifecycleState]]
        ocid: Optional[str]
        provisioning_state: Optional[Union[str, AzureResourceProvisioningState]]
        time_assigned: Optional[datetime]
        vm_ocid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                vm_ocid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.oracledatabase.models.WorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AJD = "AJD"
        APEX = "APEX"
        DW = "DW"
        OLTP = "OLTP"


    class azure.mgmt.oracledatabase.models.ZoneType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


namespace azure.mgmt.oracledatabase.operations

    class azure.mgmt.oracledatabase.operations.AutonomousDatabaseBackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                resource: AutonomousDatabaseBackup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabaseBackup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabaseBackup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabaseBackup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                properties: AutonomousDatabaseBackupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabaseBackup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabaseBackup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabaseBackup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                adbbackupid: str, 
                **kwargs: Any
            ) -> AutonomousDatabaseBackup: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> ItemPaged[AutonomousDatabaseBackup]: ...


    class azure.mgmt.oracledatabase.operations.AutonomousDatabaseCharacterSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                adbscharsetname: str, 
                **kwargs: Any
            ) -> AutonomousDatabaseCharacterSet: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[AutonomousDatabaseCharacterSet]: ...


    class azure.mgmt.oracledatabase.operations.AutonomousDatabaseNationalCharacterSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                adbsncharsetname: str, 
                **kwargs: Any
            ) -> AutonomousDatabaseNationalCharacterSet: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[AutonomousDatabaseNationalCharacterSet]: ...


    class azure.mgmt.oracledatabase.operations.AutonomousDatabaseVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                autonomousdbversionsname: str, 
                **kwargs: Any
            ) -> AutonomousDbVersion: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[AutonomousDbVersion]: ...


    class azure.mgmt.oracledatabase.operations.AutonomousDatabasesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: AutonomousDatabaseLifecycleAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_change_disaster_recovery_configuration(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: DisasterRecoveryConfigurationDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_change_disaster_recovery_configuration(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_change_disaster_recovery_configuration(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                resource: AutonomousDatabase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_failover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: PeerDbDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_failover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_failover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_restore(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: RestoreAutonomousDatabaseDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_restore(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_restore(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @distributed_trace
        def begin_shrink(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_switchover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: PeerDbDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_switchover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_switchover(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                properties: AutonomousDatabaseUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AutonomousDatabase]: ...

        @overload
        def generate_wallet(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: GenerateAutonomousDatabaseWalletDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutonomousDatabaseWalletFile: ...

        @overload
        def generate_wallet(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutonomousDatabaseWalletFile: ...

        @overload
        def generate_wallet(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutonomousDatabaseWalletFile: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                autonomousdatabasename: str, 
                **kwargs: Any
            ) -> AutonomousDatabase: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AutonomousDatabase]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AutonomousDatabase]: ...


    class azure.mgmt.oracledatabase.operations.CloudExadataInfrastructuresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_add_storage_capacity(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_configure_exascale(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                body: ConfigureExascaleCloudExadataInfrastructureDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_configure_exascale(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_configure_exascale(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                resource: CloudExadataInfrastructure, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                properties: CloudExadataInfrastructureUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudExadataInfrastructure]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> CloudExadataInfrastructure: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CloudExadataInfrastructure]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[CloudExadataInfrastructure]: ...


    class azure.mgmt.oracledatabase.operations.CloudVmClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_add_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: AddRemoveDbNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_add_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_add_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                resource: CloudVmCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: AddRemoveDbNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_remove_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_remove_vms(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                properties: CloudVmClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudVmCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> CloudVmCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CloudVmCluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[CloudVmCluster]: ...

        @overload
        def list_private_ip_addresses(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: PrivateIpAddressesFilter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[PrivateIpAddressProperties]: ...

        @overload
        def list_private_ip_addresses(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[PrivateIpAddressProperties]: ...

        @overload
        def list_private_ip_addresses(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[PrivateIpAddressProperties]: ...


    class azure.mgmt.oracledatabase.operations.DbNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                body: DbNodeAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbNode]: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbNode]: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbNode]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                dbnodeocid: str, 
                **kwargs: Any
            ) -> DbNode: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> ItemPaged[DbNode]: ...


    class azure.mgmt.oracledatabase.operations.DbServersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                dbserverocid: str, 
                **kwargs: Any
            ) -> DbServer: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                cloudexadatainfrastructurename: str, 
                **kwargs: Any
            ) -> ItemPaged[DbServer]: ...


    class azure.mgmt.oracledatabase.operations.DbSystemShapesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                dbsystemshapename: str, 
                **kwargs: Any
            ) -> DbSystemShape: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'zone', 'accept'], '2025-08-01-preview': ['shape_attribute']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_location(
                self, 
                location: str, 
                *, 
                shape_attribute: Optional[str] = ..., 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DbSystemShape]: ...


    class azure.mgmt.oracledatabase.operations.DbSystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                resource: DbSystem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbSystem]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbSystem]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbSystem]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'db_system_name']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                properties: DbSystemUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbSystem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbSystem]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbSystem]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'db_system_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                db_system_name: str, 
                **kwargs: Any
            ) -> DbSystem: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DbSystem]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[DbSystem]: ...


    class azure.mgmt.oracledatabase.operations.DbVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'location', 'dbversionsname', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                location: str, 
                dbversionsname: str, 
                **kwargs: Any
            ) -> DbVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'location', 'db_system_shape', 'db_system_id', 'storage_management', 'is_upgrade_supported', 'is_database_software_image_supported', 'shape_family', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_location(
                self, 
                location: str, 
                *, 
                db_system_id: Optional[str] = ..., 
                db_system_shape: Optional[Union[str, BaseDbSystemShapes]] = ..., 
                is_database_software_image_supported: Optional[bool] = ..., 
                is_upgrade_supported: Optional[bool] = ..., 
                shape_family: Optional[Union[str, ShapeFamilyType]] = ..., 
                storage_management: Optional[Union[str, StorageManagementType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DbVersion]: ...


    class azure.mgmt.oracledatabase.operations.DnsPrivateViewsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                dnsprivateviewocid: str, 
                **kwargs: Any
            ) -> DnsPrivateView: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[DnsPrivateView]: ...


    class azure.mgmt.oracledatabase.operations.DnsPrivateZonesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                dnsprivatezonename: str, 
                **kwargs: Any
            ) -> DnsPrivateZone: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[DnsPrivateZone]: ...


    class azure.mgmt.oracledatabase.operations.ExadbVmClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                resource: ExadbVmCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remove_vms(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                body: RemoveVirtualMachineFromExadbVmClusterDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @overload
        def begin_remove_vms(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @overload
        def begin_remove_vms(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                properties: ExadbVmClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExadbVmCluster]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                **kwargs: Any
            ) -> ExadbVmCluster: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExadbVmCluster]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ExadbVmCluster]: ...


    class azure.mgmt.oracledatabase.operations.ExascaleDbNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                body: DbNodeAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbActionResponse]: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbActionResponse]: ...

        @overload
        def begin_action(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DbActionResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name', 'exascale_db_node_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                exascale_db_node_name: str, 
                **kwargs: Any
            ) -> ExascaleDbNode: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exadb_vm_cluster_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                resource_group_name: str, 
                exadb_vm_cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExascaleDbNode]: ...


    class azure.mgmt.oracledatabase.operations.ExascaleDbStorageVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                resource: ExascaleDbStorageVault, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExascaleDbStorageVault]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExascaleDbStorageVault]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExascaleDbStorageVault]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exascale_db_storage_vault_name']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                properties: ExascaleDbStorageVaultTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExascaleDbStorageVault]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExascaleDbStorageVault]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExascaleDbStorageVault]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'exascale_db_storage_vault_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                exascale_db_storage_vault_name: str, 
                **kwargs: Any
            ) -> ExascaleDbStorageVault: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExascaleDbStorageVault]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ExascaleDbStorageVault]: ...


    class azure.mgmt.oracledatabase.operations.FlexComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-01-01-preview', params_added_on={'2025-01-01-preview': ['api_version', 'subscription_id', 'location', 'flex_component_name', 'accept']}, api_versions_list=['2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                location: str, 
                flex_component_name: str, 
                **kwargs: Any
            ) -> FlexComponent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-01-01-preview', params_added_on={'2025-01-01-preview': ['api_version', 'subscription_id', 'location', 'shape', 'accept']}, api_versions_list=['2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                location: str, 
                *, 
                shape: Optional[Union[str, SystemShapes]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FlexComponent]: ...


    class azure.mgmt.oracledatabase.operations.GiMinorVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'giversionname', 'gi_minor_version_name', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                location: str, 
                giversionname: str, 
                gi_minor_version_name: str, 
                **kwargs: Any
            ) -> GiMinorVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'giversionname', 'shape_family', 'zone', 'accept']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_parent(
                self, 
                location: str, 
                giversionname: str, 
                *, 
                shape_family: Optional[Union[str, ShapeFamily]] = ..., 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GiMinorVersion]: ...


    class azure.mgmt.oracledatabase.operations.GiVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                giversionname: str, 
                **kwargs: Any
            ) -> GiVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-12-01-preview', params_added_on={'2024-12-01-preview': ['api_version', 'subscription_id', 'location', 'shape', 'zone', 'accept'], '2025-08-01-preview': ['shape_attribute']}, api_versions_list=['2024-12-01-preview', '2025-01-01-preview', '2025-03-01', '2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_location(
                self, 
                location: str, 
                *, 
                shape: Optional[Union[str, SystemShapes]] = ..., 
                shape_attribute: Optional[str] = ..., 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GiVersion]: ...


    class azure.mgmt.oracledatabase.operations.NetworkAnchorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                resource: NetworkAnchor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkAnchor]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkAnchor]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_anchor_name']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                properties: NetworkAnchorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkAnchor]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkAnchor]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'network_anchor_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                network_anchor_name: str, 
                **kwargs: Any
            ) -> NetworkAnchor: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetworkAnchor]: ...


    class azure.mgmt.oracledatabase.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.oracledatabase.operations.OracleSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_add_azure_subscriptions(
                self, 
                body: AzureSubscriptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_azure_subscriptions(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_add_azure_subscriptions(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource: OracleSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OracleSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OracleSubscription]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OracleSubscription]: ...

        @distributed_trace
        def begin_delete(self, **kwargs: Any) -> LROPoller[None]: ...

        @distributed_trace
        def begin_list_activation_links(self, **kwargs: Any) -> LROPoller[ActivationLinks]: ...

        @distributed_trace
        def begin_list_cloud_account_details(self, **kwargs: Any) -> LROPoller[CloudAccountDetails]: ...

        @distributed_trace
        def begin_list_saas_subscription_details(self, **kwargs: Any) -> LROPoller[SaasSubscriptionDetails]: ...

        @overload
        def begin_update(
                self, 
                properties: OracleSubscriptionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OracleSubscription]: ...

        @overload
        def begin_update(
                self, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OracleSubscription]: ...

        @overload
        def begin_update(
                self, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OracleSubscription]: ...

        @distributed_trace
        def get(self, **kwargs: Any) -> OracleSubscription: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[OracleSubscription]: ...


    class azure.mgmt.oracledatabase.operations.ResourceAnchorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                resource: ResourceAnchor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceAnchor]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceAnchor]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_anchor_name']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                properties: ResourceAnchorUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceAnchor]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceAnchor]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_anchor_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                resource_anchor_name: str, 
                **kwargs: Any
            ) -> ResourceAnchor: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceAnchor]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-06-01-preview', '2025-07-01-preview', '2025-08-01-preview', '2025-08-15-preview', '2025-09-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ResourceAnchor]: ...


    class azure.mgmt.oracledatabase.operations.SystemVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                systemversionname: str, 
                **kwargs: Any
            ) -> SystemVersion: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[SystemVersion]: ...


    class azure.mgmt.oracledatabase.operations.VirtualNetworkAddressesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                resource: VirtualNetworkAddress, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkAddress]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkAddress]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualNetworkAddress]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                virtualnetworkaddressname: str, 
                **kwargs: Any
            ) -> VirtualNetworkAddress: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                cloudvmclustername: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualNetworkAddress]: ...


```