```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.servicefabric

    class azure.servicefabric.ServiceFabricClientAPIs(ServiceFabricClientAPIsOperationsMixin, SDKClient):
        config: ServiceFabricClientAPIsConfiguration
        mesh_application: MeshApplicationOperations
        mesh_code_package: MeshCodePackageOperations
        mesh_gateway: MeshGatewayOperations
        mesh_network: MeshNetworkOperations
        mesh_secret: MeshSecretOperations
        mesh_secret_value: MeshSecretValueOperations
        mesh_service: MeshServiceOperations
        mesh_service_replica: MeshServiceReplicaOperations
        mesh_volume: MeshVolumeOperations

        def __init__(
                self, 
                credentials: None, 
                base_url: str = None
            ): ...

        def add_configuration_parameter_overrides(
                self, 
                node_name: str, 
                config_parameter_override_list: list[ConfigParameterOverride], 
                force: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def add_node_tags(
                self, 
                node_name: str, 
                node_tags: list[str], 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def backup_partition(
                self, 
                partition_id: str, 
                backup_timeout: int = 10, 
                timeout: long = 60, 
                backup_storage: BackupStorageDescription = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def cancel_operation(
                self, 
                operation_id: str, 
                force: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def cancel_repair_task(
                self, 
                repair_task_cancel_description: RepairTaskCancelDescription, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def commit_image_store_upload_session(
                self, 
                session_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def copy_image_store_content(
                self, 
                image_store_copy_description: ImageStoreCopyDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_application(
                self, 
                application_description: ApplicationDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_backup_policy(
                self, 
                backup_policy_description: BackupPolicyDescription, 
                timeout: long = 60, 
                validate_connection: bool = False, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_compose_deployment(
                self, 
                create_compose_deployment_description: CreateComposeDeploymentDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_name(
                self, 
                name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_repair_task(
                self, 
                repair_task: RepairTask, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def create_service(
                self, 
                application_id: str, 
                service_description: ServiceDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_service_from_template(
                self, 
                application_id: str, 
                service_from_template_description: ServiceFromTemplateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_application(
                self, 
                application_id: str, 
                force_remove: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_backup_policy(
                self, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_image_store_content(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_image_store_upload_session(
                self, 
                session_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_name(
                self, 
                name_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_property(
                self, 
                name_id: str, 
                property_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_repair_task(
                self, 
                task_id: str, 
                version: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_service(
                self, 
                service_id: str, 
                force_remove: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def deploy_service_package_to_node(
                self, 
                node_name: str, 
                deploy_service_package_to_node_description: DeployServicePackageToNodeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_application_backup(
                self, 
                application_id: str, 
                clean_backup: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_node(
                self, 
                node_name: str, 
                timeout: long = 60, 
                deactivation_intent: Union[str, DeactivationIntent] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_partition_backup(
                self, 
                partition_id: str, 
                clean_backup: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_service_backup(
                self, 
                service_id: str, 
                clean_backup: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_application_backup(
                self, 
                application_id: str, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_node(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_partition_backup(
                self, 
                partition_id: str, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_service_backup(
                self, 
                service_id: str, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def force_approve_repair_task(
                self, 
                task_id: str, 
                version: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def get_aad_metadata(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[AadMetadataObject, ClientRawResponse]: ...

        def get_all_entities_backed_up_by_policy(
                self, 
                backup_policy_name: str, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupEntityList, ClientRawResponse]: ...

        def get_application_backup_configuration_info(
                self, 
                application_id: str, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedBackupConfigurationInfoList: ...

        def get_application_backup_list(
                self, 
                application_id: str, 
                timeout: long = 60, 
                latest: bool = False, 
                start_date_time_filter: datetime = None, 
                end_date_time_filter: datetime = None, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_application_event_list(
                self, 
                application_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ApplicationEvent], ClientRawResponse]: ...

        def get_application_health(
                self, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_applications_health_state_filter: int = 0, 
                services_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationHealth, ClientRawResponse]: ...

        def get_application_health_using_policy(
                self, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_applications_health_state_filter: int = 0, 
                services_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                application_health_policy: ApplicationHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationHealth, ClientRawResponse]: ...

        def get_application_info(
                self, 
                application_id: str, 
                exclude_application_parameters: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationInfo, ClientRawResponse]: ...

        def get_application_info_list(
                self, 
                application_definition_kind_filter: int = 0, 
                application_type_name: str = None, 
                exclude_application_parameters: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedApplicationInfoList, ClientRawResponse]: ...

        def get_application_load_info(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationLoadInfo, ClientRawResponse]: ...

        def get_application_manifest(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationTypeManifest, ClientRawResponse]: ...

        def get_application_name_info(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationNameInfo, ClientRawResponse]: ...

        def get_application_type_info_list(
                self, 
                application_type_definition_kind_filter: int = 0, 
                exclude_application_parameters: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedApplicationTypeInfoList, ClientRawResponse]: ...

        def get_application_type_info_list_by_name(
                self, 
                application_type_name: str, 
                application_type_version: str = None, 
                exclude_application_parameters: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedApplicationTypeInfoList, ClientRawResponse]: ...

        def get_application_upgrade(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationUpgradeProgressInfo, ClientRawResponse]: ...

        def get_applications_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ApplicationEvent], ClientRawResponse]: ...

        def get_backup_policy_by_name(
                self, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[BackupPolicyDescription, ClientRawResponse]: ...

        def get_backup_policy_list(
                self, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedBackupPolicyDescriptionList: ...

        def get_backups_from_backup_location(
                self, 
                get_backup_by_storage_query_description: GetBackupByStorageQueryDescription, 
                timeout: long = 60, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_chaos(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Chaos, ClientRawResponse]: ...

        def get_chaos_events(
                self, 
                continuation_token: str = None, 
                start_time_utc: str = None, 
                end_time_utc: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ChaosEventsSegment, ClientRawResponse]: ...

        def get_chaos_schedule(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ChaosScheduleDescription, ClientRawResponse]: ...

        def get_cluster_configuration(
                self, 
                configuration_api_version: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterConfiguration, ClientRawResponse]: ...

        def get_cluster_configuration_upgrade_status(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> ClusterConfigurationUpgradeStatusInfo or: ...

        def get_cluster_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ClusterEvent], ClientRawResponse]: ...

        def get_cluster_health(
                self, 
                nodes_health_state_filter: int = 0, 
                applications_health_state_filter: int = 0, 
                events_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                include_system_application_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealth, ClientRawResponse]: ...

        def get_cluster_health_chunk(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealthChunk, ClientRawResponse]: ...

        def get_cluster_health_chunk_using_policy_and_advanced_filters(
                self, 
                cluster_health_chunk_query_description: ClusterHealthChunkQueryDescription = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealthChunk, ClientRawResponse]: ...

        def get_cluster_health_using_policy(
                self, 
                nodes_health_state_filter: int = 0, 
                applications_health_state_filter: int = 0, 
                events_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                include_system_application_health_statistics: bool = False, 
                timeout: long = 60, 
                application_health_policy_map: list[ApplicationHealthPolicyMapItem] = None, 
                cluster_health_policy: ClusterHealthPolicy = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealth, ClientRawResponse]: ...

        def get_cluster_load(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterLoadInfo, ClientRawResponse]: ...

        def get_cluster_manifest(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterManifest, ClientRawResponse]: ...

        def get_cluster_upgrade_progress(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterUpgradeProgressObject, ClientRawResponse]: ...

        def get_cluster_version(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterVersion, ClientRawResponse]: ...

        def get_compose_deployment_status(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ComposeDeploymentStatusInfo, ClientRawResponse]: ...

        def get_compose_deployment_status_list(
                self, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedComposeDeploymentStatusInfoList or: ...

        def get_compose_deployment_upgrade_progress(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> ComposeDeploymentUpgradeProgressInfo or: ...

        def get_configuration_overrides(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ConfigParameterOverride], ClientRawResponse]: ...

        def get_container_logs_deployed_on_node(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str, 
                code_package_name: str, 
                tail: str = None, 
                previous: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ContainerLogs, ClientRawResponse]: ...

        def get_containers_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ContainerInstanceEvent], ClientRawResponse]: ...

        def get_correlated_event_list(
                self, 
                event_instance_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[FabricEvent], ClientRawResponse]: ...

        def get_data_loss_progress(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionDataLossProgress, ClientRawResponse]: ...

        def get_deployed_application_health(
                self, 
                node_name: str, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_service_packages_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedApplicationHealth, ClientRawResponse]: ...

        def get_deployed_application_health_using_policy(
                self, 
                node_name: str, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_service_packages_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedApplicationHealth, ClientRawResponse]: ...

        def get_deployed_application_info(
                self, 
                node_name: str, 
                application_id: str, 
                timeout: long = 60, 
                include_health_state: bool = False, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedApplicationInfo, ClientRawResponse]: ...

        def get_deployed_application_info_list(
                self, 
                node_name: str, 
                timeout: long = 60, 
                include_health_state: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedDeployedApplicationInfoList: ...

        def get_deployed_code_package_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str = None, 
                code_package_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[DeployedCodePackageInfo], ClientRawResponse]: ...

        def get_deployed_service_package_health(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                events_health_state_filter: int = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedServicePackageHealth, ClientRawResponse]: ...

        def get_deployed_service_package_health_using_policy(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                events_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedServicePackageHealth, ClientRawResponse]: ...

        def get_deployed_service_package_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> list[DeployedServicePackageInfo]: ...

        def get_deployed_service_package_info_list_by_name(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> list[DeployedServicePackageInfo]: ...

        def get_deployed_service_replica_detail_info(
                self, 
                node_name: str, 
                partition_id: str, 
                replica_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DeployedServiceReplicaDetailInfo: ...

        def get_deployed_service_replica_detail_info_by_partition_id(
                self, 
                node_name: str, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DeployedServiceReplicaDetailInfo: ...

        def get_deployed_service_replica_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                partition_id: str = None, 
                service_manifest_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> list[DeployedServiceReplicaInfo]: ...

        def get_deployed_service_type_info_by_name(
                self, 
                node_name: str, 
                application_id: str, 
                service_type_name: str, 
                service_manifest_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[DeployedServiceTypeInfo], ClientRawResponse]: ...

        def get_deployed_service_type_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[DeployedServiceTypeInfo], ClientRawResponse]: ...

        def get_fault_operation_list(
                self, 
                type_filter: int = 65535, 
                state_filter: int = 65535, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[OperationStatus], ClientRawResponse]: ...

        def get_image_store_content(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ImageStoreContent, ClientRawResponse]: ...

        def get_image_store_folder_size(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[FolderSizeInfo, ClientRawResponse]: ...

        def get_image_store_info(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ImageStoreInfo, ClientRawResponse]: ...

        def get_image_store_root_content(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ImageStoreContent, ClientRawResponse]: ...

        def get_image_store_root_folder_size(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[FolderSizeInfo, ClientRawResponse]: ...

        def get_image_store_upload_session_by_id(
                self, 
                session_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UploadSession, ClientRawResponse]: ...

        def get_image_store_upload_session_by_path(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UploadSession, ClientRawResponse]: ...

        def get_loaded_partition_info_list(
                self, 
                metric_name: str, 
                service_name: str = None, 
                ordering: Union[str, Ordering] = "Desc", 
                max_results: long = 0, 
                continuation_token: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> LoadedPartitionInformationResultList or: ...

        def get_name_exists_info(
                self, 
                name_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get_node_event_list(
                self, 
                node_name: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[NodeEvent], ClientRawResponse]: ...

        def get_node_health(
                self, 
                node_name: str, 
                events_health_state_filter: int = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeHealth, ClientRawResponse]: ...

        def get_node_health_using_policy(
                self, 
                node_name: str, 
                events_health_state_filter: int = 0, 
                cluster_health_policy: ClusterHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeHealth, ClientRawResponse]: ...

        def get_node_info(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeInfo, ClientRawResponse]: ...

        def get_node_info_list(
                self, 
                continuation_token: str = None, 
                node_status_filter: Union[str, NodeStatusFilter] = "default", 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedNodeInfoList, ClientRawResponse]: ...

        def get_node_load_info(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeLoadInfo, ClientRawResponse]: ...

        def get_node_transition_progress(
                self, 
                node_name: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeTransitionProgress, ClientRawResponse]: ...

        def get_nodes_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[NodeEvent], ClientRawResponse]: ...

        def get_partition_backup_configuration_info(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PartitionBackupConfigurationInfo: ...

        def get_partition_backup_list(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                latest: bool = False, 
                start_date_time_filter: datetime = None, 
                end_date_time_filter: datetime = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_partition_backup_progress(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[BackupProgressInfo, ClientRawResponse]: ...

        def get_partition_event_list(
                self, 
                partition_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[PartitionEvent], ClientRawResponse]: ...

        def get_partition_health(
                self, 
                partition_id: str, 
                events_health_state_filter: int = 0, 
                replicas_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionHealth, ClientRawResponse]: ...

        def get_partition_health_using_policy(
                self, 
                partition_id: str, 
                events_health_state_filter: int = 0, 
                replicas_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionHealth, ClientRawResponse]: ...

        def get_partition_info(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServicePartitionInfo, ClientRawResponse]: ...

        def get_partition_info_list(
                self, 
                service_id: str, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedServicePartitionInfoList, ClientRawResponse]: ...

        def get_partition_load_information(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionLoadInformation, ClientRawResponse]: ...

        def get_partition_replica_event_list(
                self, 
                partition_id: str, 
                replica_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ReplicaEvent], ClientRawResponse]: ...

        def get_partition_replicas_event_list(
                self, 
                partition_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ReplicaEvent], ClientRawResponse]: ...

        def get_partition_restart_progress(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionRestartProgress, ClientRawResponse]: ...

        def get_partition_restore_progress(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RestoreProgressInfo, ClientRawResponse]: ...

        def get_partitions_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[PartitionEvent], ClientRawResponse]: ...

        def get_property_info(
                self, 
                name_id: str, 
                property_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PropertyInfo, ClientRawResponse]: ...

        def get_property_info_list(
                self, 
                name_id: str, 
                include_values: bool = False, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedPropertyInfoList, ClientRawResponse]: ...

        def get_provisioned_fabric_code_version_info_list(
                self, 
                code_version: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[FabricCodeVersionInfo], ClientRawResponse]: ...

        def get_provisioned_fabric_config_version_info_list(
                self, 
                config_version: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[FabricConfigVersionInfo], ClientRawResponse]: ...

        def get_quorum_loss_progress(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionQuorumLossProgress, ClientRawResponse]: ...

        def get_repair_task_list(
                self, 
                task_id_filter: str = None, 
                state_filter: int = None, 
                executor_filter: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[RepairTask], ClientRawResponse]: ...

        def get_replica_health(
                self, 
                partition_id: str, 
                replica_id: str, 
                events_health_state_filter: int = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ReplicaHealth, ClientRawResponse]: ...

        def get_replica_health_using_policy(
                self, 
                partition_id: str, 
                replica_id: str, 
                events_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ReplicaHealth, ClientRawResponse]: ...

        def get_replica_info(
                self, 
                partition_id: str, 
                replica_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ReplicaInfo, ClientRawResponse]: ...

        def get_replica_info_list(
                self, 
                partition_id: str, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedReplicaInfoList, ClientRawResponse]: ...

        def get_service_backup_configuration_info(
                self, 
                service_id: str, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedBackupConfigurationInfoList: ...

        def get_service_backup_list(
                self, 
                service_id: str, 
                timeout: long = 60, 
                latest: bool = False, 
                start_date_time_filter: datetime = None, 
                end_date_time_filter: datetime = None, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_service_description(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceDescription, ClientRawResponse]: ...

        def get_service_event_list(
                self, 
                service_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ServiceEvent], ClientRawResponse]: ...

        def get_service_health(
                self, 
                service_id: str, 
                events_health_state_filter: int = 0, 
                partitions_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceHealth, ClientRawResponse]: ...

        def get_service_health_using_policy(
                self, 
                service_id: str, 
                events_health_state_filter: int = 0, 
                partitions_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceHealth, ClientRawResponse]: ...

        def get_service_info(
                self, 
                application_id: str, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceInfo, ClientRawResponse]: ...

        def get_service_info_list(
                self, 
                application_id: str, 
                service_type_name: str = None, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedServiceInfoList, ClientRawResponse]: ...

        def get_service_manifest(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                service_manifest_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceTypeManifest, ClientRawResponse]: ...

        def get_service_name_info(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceNameInfo, ClientRawResponse]: ...

        def get_service_type_info_by_name(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                service_type_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceTypeInfo, ClientRawResponse]: ...

        def get_service_type_info_list(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ServiceTypeInfo], ClientRawResponse]: ...

        def get_services_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ServiceEvent], ClientRawResponse]: ...

        def get_sub_name_info_list(
                self, 
                name_id: str, 
                recursive: bool = False, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedSubNameInfoList, ClientRawResponse]: ...

        def get_unplaced_replica_information(
                self, 
                service_id: str, 
                partition_id: str = None, 
                only_query_primaries: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UnplacedReplicaInformation, ClientRawResponse]: ...

        def get_upgrade_orchestration_service_state(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> UpgradeOrchestrationServiceState: ...

        def invoke_container_api(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str, 
                code_package_name: str, 
                code_package_instance_id: str, 
                container_api_request_body: ContainerApiRequestBody, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ContainerApiResponse, ClientRawResponse]: ...

        def invoke_infrastructure_command(
                self, 
                command: str, 
                service_id: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[str, ClientRawResponse]: ...

        def invoke_infrastructure_query(
                self, 
                command: str, 
                service_id: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[str, ClientRawResponse]: ...

        def move_auxiliary_replica(
                self, 
                service_id: str, 
                partition_id: str, 
                current_node_name: str = None, 
                new_node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def move_instance(
                self, 
                service_id: str, 
                partition_id: str, 
                current_node_name: str = None, 
                new_node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def move_primary_replica(
                self, 
                partition_id: str, 
                node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def move_secondary_replica(
                self, 
                partition_id: str, 
                current_node_name: str, 
                new_node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def post_chaos_schedule(
                self, 
                timeout: long = 60, 
                version: int = None, 
                schedule: ChaosSchedule = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def provision_application_type(
                self, 
                provision_application_type_description_base_required_body_param, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def provision_cluster(
                self, 
                timeout: long = 60, 
                code_file_path: str = None, 
                cluster_manifest_file_path: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def put_property(
                self, 
                name_id: str, 
                property_description: PropertyDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_all_partitions(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_partition(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_service_partitions(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_system_partitions(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_compose_deployment(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_configuration_overrides(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_node_state(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_node_tags(
                self, 
                node_name: str, 
                node_tags: list[str], 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_replica(
                self, 
                node_name: str, 
                partition_id: str, 
                replica_id: str, 
                force_remove: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_application_health(
                self, 
                application_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_cluster_health(
                self, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_deployed_application_health(
                self, 
                node_name: str, 
                application_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_deployed_service_package_health(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_node_health(
                self, 
                node_name: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_partition_health(
                self, 
                partition_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_replica_health(
                self, 
                partition_id: str, 
                replica_id: str, 
                health_information: HealthInformation, 
                service_kind: Union[str, ReplicaHealthReportServiceKind] = "Stateful", 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_service_health(
                self, 
                service_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def reset_partition_load(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resolve_service(
                self, 
                service_id: str, 
                partition_key_type: int = None, 
                partition_key_value: str = None, 
                previous_rsp_version: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ResolvedServicePartition, ClientRawResponse]: ...

        def restart_deployed_code_package(
                self, 
                node_name: str, 
                application_id: str, 
                restart_deployed_code_package_description: RestartDeployedCodePackageDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def restart_node(
                self, 
                node_name: str, 
                node_instance_id: str = "0", 
                timeout: long = 60, 
                create_fabric_dump: Union[str, CreateFabricDump] = "False", 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def restart_replica(
                self, 
                node_name: str, 
                partition_id: str, 
                replica_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def restore_partition(
                self, 
                partition_id: str, 
                restore_partition_description: RestorePartitionDescription, 
                restore_timeout: int = 10, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_application_backup(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_application_upgrade(
                self, 
                application_id: str, 
                upgrade_domain_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_cluster_upgrade(
                self, 
                upgrade_domain: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_partition_backup(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_service_backup(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def rollback_application_upgrade(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def rollback_cluster_upgrade(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def set_upgrade_orchestration_service_state(
                self, 
                timeout: long = 60, 
                service_state: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> UpgradeOrchestrationServiceStateSummary or: ...

        def start_application_upgrade(
                self, 
                application_id: str, 
                application_upgrade_description: ApplicationUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_chaos(
                self, 
                chaos_parameters: ChaosParameters, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_cluster_configuration_upgrade(
                self, 
                cluster_configuration_upgrade_description: ClusterConfigurationUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_cluster_upgrade(
                self, 
                start_cluster_upgrade_description: StartClusterUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_compose_deployment_upgrade(
                self, 
                deployment_name: str, 
                compose_deployment_upgrade_description: ComposeDeploymentUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_data_loss(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                data_loss_mode: Union[str, DataLossMode], 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_node_transition(
                self, 
                node_name: str, 
                operation_id: str, 
                node_transition_type: Union[str, NodeTransitionType], 
                node_instance_id: str, 
                stop_duration_in_seconds: int, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_partition_restart(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                restart_partition_mode: Union[str, RestartPartitionMode], 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_quorum_loss(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                quorum_loss_mode: Union[str, QuorumLossMode], 
                quorum_loss_duration: int, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_rollback_compose_deployment_upgrade(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def stop_chaos(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def submit_property_batch(
                self, 
                name_id: str, 
                timeout: long = 60, 
                operations: list[PropertyBatchOperation] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PropertyBatchInfo, ClientRawResponse]: ...

        def suspend_application_backup(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def suspend_partition_backup(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def suspend_service_backup(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def toggle_verbose_service_placement_health_reporting(
                self, 
                enabled: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def unprovision_application_type(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                timeout: long = 60, 
                async_parameter: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def unprovision_cluster(
                self, 
                timeout: long = 60, 
                code_version: str = None, 
                config_version: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_application(
                self, 
                application_id: str, 
                application_update_description: ApplicationUpdateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_application_upgrade(
                self, 
                application_id: str, 
                application_upgrade_update_description: ApplicationUpgradeUpdateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_backup_policy(
                self, 
                backup_policy_description: BackupPolicyDescription, 
                backup_policy_name: str, 
                timeout: long = 60, 
                validate_connection: bool = False, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_cluster_upgrade(
                self, 
                update_cluster_upgrade_description: UpdateClusterUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_partition_load(
                self, 
                partition_metric_load_description_list: list[PartitionMetricLoadDescription], 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedUpdatePartitionLoadResultList: ...

        def update_repair_execution_state(
                self, 
                repair_task: RepairTask, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def update_repair_task_health_policy(
                self, 
                repair_task_update_health_policy_description: RepairTaskUpdateHealthPolicyDescription, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def update_service(
                self, 
                service_id: str, 
                service_update_description: ServiceUpdateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def upload_file(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def upload_file_chunk(
                self, 
                content_path: str, 
                session_id: str, 
                content_range: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def validate_cluster_upgrade(
                self, 
                start_cluster_upgrade_description: StartClusterUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ValidateClusterUpgradeResult, ClientRawResponse]: ...


    class azure.servicefabric.ServiceFabricClientAPIsConfiguration(Configuration):
        property enable_http_logger: 
        property user_agent: str    # Read-only

        def __init__(
                self, 
                credentials: None, 
                base_url: str = None
            ): ...


namespace azure.servicefabric.models

    class azure.servicefabric.models.AadMetadata(Model):

        def __init__(
                self, 
                *, 
                authority: str = ..., 
                client: str = ..., 
                cluster: str = ..., 
                login: str = ..., 
                redirect: str = ..., 
                tenant: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AadMetadataObject(Model):

        def __init__(
                self, 
                *, 
                metadata = ..., 
                type: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AddRemoveIncrementalNamedPartitionScalingMechanism(ScalingMechanismDescription):

        def __init__(
                self, 
                *, 
                max_partition_count: int, 
                min_partition_count: int, 
                scale_increment: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AddRemoveReplicaScalingMechanism(AutoScalingMechanism):

        def __init__(
                self, 
                *, 
                max_count: int, 
                min_count: int, 
                scale_increment: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AnalysisEventMetadata(Model):

        def __init__(
                self, 
                *, 
                delay = ..., 
                duration = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationBackupConfigurationInfo(BackupConfigurationInfo):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                policy_inherited_from = ..., 
                policy_name: str = ..., 
                suspension_info = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationBackupEntity(BackupEntity):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationCapacityDescription(Model):

        def __init__(
                self, 
                *, 
                application_metrics = ..., 
                maximum_nodes: int = 0, 
                minimum_nodes: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationContainerInstanceExitedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                category: str = ..., 
                code_package_name: str, 
                container_name: str, 
                entry_point_type: str, 
                event_instance_id: str, 
                exit_code: int, 
                has_correlated_events: bool = ..., 
                host_id: str, 
                image_name: str, 
                is_exclusive: bool, 
                service_name: str, 
                service_package_activation_id: str, 
                service_package_name: str, 
                start_time, 
                time_stamp, 
                unexpected_termination: bool, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationCreatedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_definition_kind: str, 
                application_id: str, 
                application_type_name: str, 
                application_type_version: str, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationDefinitionKind(str, Enum):
        compose = "Compose"
        invalid = "Invalid"
        service_fabric_application_description = "ServiceFabricApplicationDescription"


    class azure.servicefabric.models.ApplicationDeletedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_type_name: str, 
                application_type_version: str, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationDescription(Model):

        def __init__(
                self, 
                *, 
                application_capacity = ..., 
                managed_application_identity = ..., 
                name: str, 
                parameter_list = ..., 
                type_name: str, 
                type_version: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationEvent(FabricEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                deployed_application_health_states = ..., 
                health_events = ..., 
                health_statistics = ..., 
                name: str = ..., 
                service_health_states = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_name: str = ..., 
                description: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthPolicies(Model):

        def __init__(
                self, 
                *, 
                application_health_policy_map = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthPolicy(Model):

        def __init__(
                self, 
                *, 
                consider_warning_as_error: bool = False, 
                default_service_type_health_policy = ..., 
                max_percent_unhealthy_deployed_applications: int = 0, 
                service_type_health_policy_map = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthPolicyMapItem(Model):

        def __init__(
                self, 
                *, 
                key: str, 
                value, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthPolicyMapObject(Model):

        def __init__(
                self, 
                *, 
                application_health_policy_map = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthReportExpiredEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_instance_id: int, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthState(EntityHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthStateChunk(EntityHealthStateChunk):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                application_type_name: str = ..., 
                deployed_application_health_state_chunks = ..., 
                health_state = ..., 
                service_health_state_chunks = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthStateChunkList(EntityHealthStateChunkList):

        def __init__(
                self, 
                *, 
                items = ..., 
                total_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationHealthStateFilter(Model):

        def __init__(
                self, 
                *, 
                application_name_filter: str = ..., 
                application_type_name_filter: str = ..., 
                deployed_application_filters = ..., 
                health_state_filter: int = 0, 
                service_filters = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationInfo(Model):

        def __init__(
                self, 
                *, 
                application_definition_kind = ..., 
                health_state = ..., 
                id: str = ..., 
                managed_application_identity = ..., 
                name: str = ..., 
                parameters = ..., 
                status = ..., 
                type_name: str = ..., 
                type_version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationLoadInfo(Model):

        def __init__(
                self, 
                *, 
                application_load_metric_information = ..., 
                id: str = ..., 
                maximum_nodes: int = ..., 
                minimum_nodes: int = ..., 
                node_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationLoadMetricInformation(Model):

        def __init__(
                self, 
                *, 
                application_capacity: int = ..., 
                application_load: int = ..., 
                name: str = ..., 
                reservation_capacity: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationMetricDescription(Model):

        def __init__(
                self, 
                *, 
                maximum_capacity: int = ..., 
                name: str = ..., 
                reservation_capacity: int = ..., 
                total_application_capacity: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationNameInfo(Model):

        def __init__(
                self, 
                *, 
                id: str = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationNewHealthReportEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_instance_id: int, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationPackageCleanupPolicy(str, Enum):
        automatic = "Automatic"
        default = "Default"
        invalid = "Invalid"
        manual = "Manual"


    class azure.servicefabric.models.ApplicationParameter(Model):

        def __init__(
                self, 
                *, 
                key: str, 
                value: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationProcessExitedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                category: str = ..., 
                code_package_name: str, 
                entry_point_type: str, 
                event_instance_id: str, 
                exe_name: str, 
                exit_code: int, 
                has_correlated_events: bool = ..., 
                host_id: str, 
                is_exclusive: bool, 
                process_id: int, 
                service_name: str, 
                service_package_activation_id: str, 
                service_package_name: str, 
                start_time, 
                time_stamp, 
                unexpected_termination: bool, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationResourceDescription(Model):
        health_state: Union[str, HealthState]
        service_names: list[str]
        status: Union[str, ResourceStatus]
        status_details: str
        unhealthy_evaluation: str

        def __init__(
                self, 
                *, 
                debug_params: str = ..., 
                description: str = ..., 
                diagnostics = ..., 
                identity = ..., 
                name: str, 
                services = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationResourceUpgradeProgressInfo(Model):

        def __init__(
                self, 
                *, 
                application_upgrade_status_details: str = ..., 
                failure_timestamp_utc: str = ..., 
                name: str = ..., 
                percent_completed: str = ..., 
                rolling_upgrade_mode = "Monitored", 
                service_upgrade_progress = ..., 
                start_timestamp_utc: str = ..., 
                target_application_type_version: str = ..., 
                upgrade_duration: str = "PT0H2M0S", 
                upgrade_replica_set_check_timeout_in_seconds: int = 42949672925, 
                upgrade_state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationResourceUpgradeState(str, Enum):
        completed_rollback = "CompletedRollback"
        completed_rollforward = "CompletedRollforward"
        failed = "Failed"
        invalid = "Invalid"
        provisioning_target = "ProvisioningTarget"
        rolling_back = "RollingBack"
        rolling_forward = "RollingForward"
        unprovisioning_current = "UnprovisioningCurrent"
        unprovisioning_target = "UnprovisioningTarget"


    class azure.servicefabric.models.ApplicationScopedVolume(VolumeReference):

        def __init__(
                self, 
                *, 
                creation_parameters, 
                destination_path: str, 
                name: str, 
                read_only: bool = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationScopedVolumeCreationParameters(Model):

        def __init__(
                self, 
                *, 
                description: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationScopedVolumeCreationParametersServiceFabricVolumeDisk(ApplicationScopedVolumeCreationParameters):

        def __init__(
                self, 
                *, 
                description: str = ..., 
                size_disk, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationScopedVolumeKind(str, Enum):
        service_fabric_volume_disk = "ServiceFabricVolumeDisk"


    class azure.servicefabric.models.ApplicationStatus(str, Enum):
        creating = "Creating"
        deleting = "Deleting"
        failed = "Failed"
        invalid = "Invalid"
        ready = "Ready"
        upgrading = "Upgrading"


    class azure.servicefabric.models.ApplicationTypeApplicationsHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_type_name: str = ..., 
                description: str = ..., 
                max_percent_unhealthy_applications: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationTypeDefinitionKind(str, Enum):
        compose = "Compose"
        invalid = "Invalid"
        service_fabric_application_package = "ServiceFabricApplicationPackage"


    class azure.servicefabric.models.ApplicationTypeHealthPolicyMapItem(Model):

        def __init__(
                self, 
                *, 
                key: str, 
                value: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationTypeImageStorePath(Model):

        def __init__(
                self, 
                *, 
                application_type_build_path: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationTypeInfo(Model):

        def __init__(
                self, 
                *, 
                application_type_definition_kind = ..., 
                default_parameter_list = ..., 
                name: str = ..., 
                status = ..., 
                status_details: str = ..., 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationTypeManifest(Model):

        def __init__(
                self, 
                *, 
                manifest: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationTypeStatus(str, Enum):
        available = "Available"
        failed = "Failed"
        invalid = "Invalid"
        provisioning = "Provisioning"
        unprovisioning = "Unprovisioning"


    class azure.servicefabric.models.ApplicationUpdateDescription(Model):

        def __init__(
                self, 
                *, 
                application_metrics = ..., 
                flags: str = ..., 
                maximum_nodes: int = 0, 
                minimum_nodes: int = ..., 
                remove_application_capacity: bool = False, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeCompletedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_type_name: str, 
                application_type_version: str, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                overall_upgrade_elapsed_time_in_ms: float, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeDescription(Model):

        def __init__(
                self, 
                *, 
                application_health_policy = ..., 
                force_restart: bool = ..., 
                instance_close_delay_duration_in_seconds: int = ..., 
                managed_application_identity = ..., 
                monitoring_policy = ..., 
                name: str, 
                parameters = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                sort_order = "Default", 
                target_application_type_version: str, 
                upgrade_kind = "Rolling", 
                upgrade_replica_set_check_timeout_in_seconds: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeDomainCompletedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_type_name: str, 
                application_type_version: str, 
                category: str = ..., 
                current_application_type_version: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                time_stamp, 
                upgrade_domain_elapsed_time_in_ms: float, 
                upgrade_domains: str, 
                upgrade_state: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeProgressInfo(Model):

        def __init__(
                self, 
                *, 
                current_upgrade_domain_progress = ..., 
                current_upgrade_units_progress = ..., 
                failure_reason = ..., 
                failure_timestamp_utc: str = ..., 
                is_node_by_node: bool = False, 
                name: str = ..., 
                next_upgrade_domain: str = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                start_timestamp_utc: str = ..., 
                target_application_type_version: str = ..., 
                type_name: str = ..., 
                unhealthy_evaluations = ..., 
                upgrade_description = ..., 
                upgrade_domain_duration_in_milliseconds: str = ..., 
                upgrade_domain_progress_at_failure = ..., 
                upgrade_domains = ..., 
                upgrade_duration_in_milliseconds: str = ..., 
                upgrade_state = ..., 
                upgrade_status_details: str = ..., 
                upgrade_units = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeRollbackCompletedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_type_name: str, 
                application_type_version: str, 
                category: str = ..., 
                event_instance_id: str, 
                failure_reason: str, 
                has_correlated_events: bool = ..., 
                overall_upgrade_elapsed_time_in_ms: float, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeRollbackStartedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_type_name: str, 
                application_type_version: str, 
                category: str = ..., 
                current_application_type_version: str, 
                event_instance_id: str, 
                failure_reason: str, 
                has_correlated_events: bool = ..., 
                overall_upgrade_elapsed_time_in_ms: float, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeStartedEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_type_name: str, 
                application_type_version: str, 
                category: str = ..., 
                current_application_type_version: str, 
                event_instance_id: str, 
                failure_action: str, 
                has_correlated_events: bool = ..., 
                rolling_upgrade_mode: str, 
                time_stamp, 
                upgrade_type: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationUpgradeUpdateDescription(Model):

        def __init__(
                self, 
                *, 
                application_health_policy = ..., 
                name: str, 
                update_description = ..., 
                upgrade_kind = "Rolling", 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ApplicationsHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_applications: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AutoScalingMechanism(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.AutoScalingMechanismKind(str, Enum):
        add_remove_replica = "AddRemoveReplica"


    class azure.servicefabric.models.AutoScalingMetric(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.AutoScalingMetricKind(str, Enum):
        resource = "Resource"


    class azure.servicefabric.models.AutoScalingPolicy(Model):

        def __init__(
                self, 
                *, 
                mechanism, 
                name: str, 
                trigger, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AutoScalingResourceMetric(AutoScalingMetric):

        def __init__(
                self, 
                *, 
                name, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AutoScalingResourceMetricName(str, Enum):
        cpu = "cpu"
        memory_in_gb = "memoryInGB"


    class azure.servicefabric.models.AutoScalingTrigger(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.AutoScalingTriggerKind(str, Enum):
        average_load = "AverageLoad"


    class azure.servicefabric.models.AverageLoadScalingTrigger(AutoScalingTrigger):

        def __init__(
                self, 
                *, 
                lower_load_threshold: float, 
                metric, 
                scale_interval_in_seconds: int, 
                upper_load_threshold: float, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AveragePartitionLoadScalingTrigger(ScalingTriggerDescription):

        def __init__(
                self, 
                *, 
                lower_load_threshold: str, 
                metric_name: str, 
                scale_interval_in_seconds: int, 
                upper_load_threshold: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AverageServiceLoadScalingTrigger(ScalingTriggerDescription):

        def __init__(
                self, 
                *, 
                lower_load_threshold: str, 
                metric_name: str, 
                scale_interval_in_seconds: int, 
                upper_load_threshold: str, 
                use_only_primary_load: bool, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AzureBlobBackupStorageDescription(BackupStorageDescription):

        def __init__(
                self, 
                *, 
                connection_string: str, 
                container_name: str, 
                friendly_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.AzureInternalMonitoringPipelineSinkDescription(DiagnosticsSinkProperties):

        def __init__(
                self, 
                *, 
                account_name: str = ..., 
                auto_key_config_url: str = ..., 
                description: str = ..., 
                fluentd_config_url: str = ..., 
                ma_config_url: str = ..., 
                name: str = ..., 
                namespace: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupConfigurationInfo(Model):

        def __init__(
                self, 
                *, 
                policy_inherited_from = ..., 
                policy_name: str = ..., 
                suspension_info = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupEntity(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.BackupEntityKind(str, Enum):
        application = "Application"
        invalid = "Invalid"
        partition = "Partition"
        service = "Service"


    class azure.servicefabric.models.BackupInfo(Model):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                backup_chain_id: str = ..., 
                backup_id: str = ..., 
                backup_location: str = ..., 
                backup_type = ..., 
                creation_time_utc = ..., 
                epoch_of_last_backup_record = ..., 
                failure_error = ..., 
                lsn_of_last_backup_record: str = ..., 
                partition_information = ..., 
                service_manifest_version: str = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupPartitionDescription(Model):

        def __init__(
                self, 
                *, 
                backup_storage = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupPolicyDescription(Model):

        def __init__(
                self, 
                *, 
                auto_restore_on_data_loss: bool, 
                max_incremental_backups: int, 
                name: str, 
                retention_policy = ..., 
                schedule, 
                storage, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupPolicyScope(str, Enum):
        application = "Application"
        invalid = "Invalid"
        partition = "Partition"
        service = "Service"


    class azure.servicefabric.models.BackupProgressInfo(Model):

        def __init__(
                self, 
                *, 
                backup_id: str = ..., 
                backup_location: str = ..., 
                backup_state = ..., 
                epoch_of_last_backup_record = ..., 
                failure_error = ..., 
                lsn_of_last_backup_record: str = ..., 
                time_stamp_utc = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupScheduleDescription(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.BackupScheduleFrequencyType(str, Enum):
        daily = "Daily"
        invalid = "Invalid"
        weekly = "Weekly"


    class azure.servicefabric.models.BackupScheduleKind(str, Enum):
        frequency_based = "FrequencyBased"
        invalid = "Invalid"
        time_based = "TimeBased"


    class azure.servicefabric.models.BackupState(str, Enum):
        accepted = "Accepted"
        backup_in_progress = "BackupInProgress"
        failure = "Failure"
        invalid = "Invalid"
        success = "Success"
        timeout = "Timeout"


    class azure.servicefabric.models.BackupStorageDescription(Model):

        def __init__(
                self, 
                *, 
                friendly_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupStorageKind(str, Enum):
        azure_blob_store = "AzureBlobStore"
        dsms_azure_blob_store = "DsmsAzureBlobStore"
        file_share = "FileShare"
        invalid = "Invalid"
        managed_identity_azure_blob_store = "ManagedIdentityAzureBlobStore"


    class azure.servicefabric.models.BackupSuspensionInfo(Model):

        def __init__(
                self, 
                *, 
                is_suspended: bool = ..., 
                suspension_inherited_from = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BackupSuspensionScope(str, Enum):
        application = "Application"
        invalid = "Invalid"
        partition = "Partition"
        service = "Service"


    class azure.servicefabric.models.BackupType(str, Enum):
        full = "Full"
        incremental = "Incremental"
        invalid = "Invalid"


    class azure.servicefabric.models.BasicRetentionPolicyDescription(RetentionPolicyDescription):

        def __init__(
                self, 
                *, 
                minimum_number_of_backups: int = ..., 
                retention_duration, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.BinaryPropertyValue(PropertyValue):

        def __init__(
                self, 
                *, 
                data, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.Chaos(Model):

        def __init__(
                self, 
                *, 
                chaos_parameters = ..., 
                schedule_status = ..., 
                status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosCodePackageRestartScheduledEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                category: str = ..., 
                code_package_name: str, 
                event_instance_id: str, 
                fault_group_id: str, 
                fault_id: str, 
                has_correlated_events: bool = ..., 
                node_name: str, 
                service_manifest_name: str, 
                service_package_activation_id: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosContext(Model):

        def __init__(
                self, 
                *, 
                map = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosEvent(Model):

        def __init__(
                self, 
                *, 
                time_stamp_utc, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosEventKind(str, Enum):
        executing_faults = "ExecutingFaults"
        invalid = "Invalid"
        started = "Started"
        stopped = "Stopped"
        test_error = "TestError"
        validation_failed = "ValidationFailed"
        waiting = "Waiting"


    class azure.servicefabric.models.ChaosEventWrapper(Model):

        def __init__(
                self, 
                *, 
                chaos_event = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosEventsSegment(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                history = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosNodeRestartScheduledEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fault_group_id: str, 
                fault_id: str, 
                has_correlated_events: bool = ..., 
                node_instance_id: int, 
                node_name: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosParameters(Model):

        def __init__(
                self, 
                *, 
                chaos_target_filter = ..., 
                cluster_health_policy = ..., 
                context = ..., 
                enable_move_replica_faults: bool = True, 
                max_cluster_stabilization_timeout_in_seconds: int = 60, 
                max_concurrent_faults: int = 1, 
                time_to_run_in_seconds: str = "4294967295", 
                wait_time_between_faults_in_seconds: int = 20, 
                wait_time_between_iterations_in_seconds: int = 30, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosParametersDictionaryItem(Model):

        def __init__(
                self, 
                *, 
                key: str, 
                value, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosPartitionPrimaryMoveScheduledEvent(PartitionEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fault_group_id: str, 
                fault_id: str, 
                forced_move: bool, 
                has_correlated_events: bool = ..., 
                node_to: str, 
                partition_id: str, 
                service_name: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosPartitionSecondaryMoveScheduledEvent(PartitionEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                destination_node: str, 
                event_instance_id: str, 
                fault_group_id: str, 
                fault_id: str, 
                forced_move: bool, 
                has_correlated_events: bool = ..., 
                partition_id: str, 
                service_name: str, 
                source_node: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosReplicaRemovalScheduledEvent(ReplicaEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fault_group_id: str, 
                fault_id: str, 
                has_correlated_events: bool = ..., 
                partition_id: str, 
                replica_id: int, 
                service_uri: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosReplicaRestartScheduledEvent(ReplicaEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fault_group_id: str, 
                fault_id: str, 
                has_correlated_events: bool = ..., 
                partition_id: str, 
                replica_id: int, 
                service_uri: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosSchedule(Model):

        def __init__(
                self, 
                *, 
                chaos_parameters_dictionary = ..., 
                expiry_date = "9999-12-31T23:59:59.999Z", 
                jobs = ..., 
                start_date = "1601-01-01T00:00:00Z", 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosScheduleDescription(Model):

        def __init__(
                self, 
                *, 
                schedule = ..., 
                version: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosScheduleJob(Model):

        def __init__(
                self, 
                *, 
                chaos_parameters: str = ..., 
                days = ..., 
                times = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosScheduleJobActiveDaysOfWeek(Model):

        def __init__(
                self, 
                *, 
                friday: bool = False, 
                monday: bool = False, 
                saturday: bool = False, 
                sunday: bool = False, 
                thursday: bool = False, 
                tuesday: bool = False, 
                wednesday: bool = False, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosScheduleStatus(str, Enum):
        active = "Active"
        expired = "Expired"
        invalid = "Invalid"
        pending = "Pending"
        stopped = "Stopped"


    class azure.servicefabric.models.ChaosStartedEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                chaos_context: str, 
                cluster_health_policy: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                included_application_list: str, 
                included_node_type_list: str, 
                max_cluster_stabilization_timeout_in_seconds: float, 
                max_concurrent_faults: int, 
                move_replica_fault_enabled: bool, 
                time_stamp, 
                time_to_run_in_seconds: float, 
                wait_time_between_faults_in_seconds: float, 
                wait_time_between_iterations_in_seconds: float, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosStatus(str, Enum):
        invalid = "Invalid"
        running = "Running"
        stopped = "Stopped"


    class azure.servicefabric.models.ChaosStoppedEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                reason: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ChaosTargetFilter(Model):

        def __init__(
                self, 
                *, 
                application_inclusion_list = ..., 
                node_type_inclusion_list = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CheckExistsPropertyBatchOperation(PropertyBatchOperation):

        def __init__(
                self, 
                *, 
                exists: bool, 
                property_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CheckSequencePropertyBatchOperation(PropertyBatchOperation):

        def __init__(
                self, 
                *, 
                property_name: str, 
                sequence_number: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CheckValuePropertyBatchOperation(PropertyBatchOperation):

        def __init__(
                self, 
                *, 
                property_name: str, 
                value, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterConfiguration(Model):

        def __init__(
                self, 
                *, 
                cluster_configuration: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterConfigurationUpgradeDescription(Model):

        def __init__(
                self, 
                *, 
                application_health_policies = ..., 
                cluster_config: str, 
                health_check_retry_timeout = "PT0H0M0S", 
                health_check_stable_duration_in_seconds = "PT0H0M0S", 
                health_check_wait_duration_in_seconds = "PT0H0M0S", 
                max_percent_delta_unhealthy_nodes: int = 0, 
                max_percent_unhealthy_applications: int = 0, 
                max_percent_unhealthy_nodes: int = 0, 
                max_percent_upgrade_domain_delta_unhealthy_nodes: int = 0, 
                upgrade_domain_timeout_in_seconds = "PT0H0M0S", 
                upgrade_timeout_in_seconds = "PT0H0M0S", 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterConfigurationUpgradeStatusInfo(Model):

        def __init__(
                self, 
                *, 
                config_version: str = ..., 
                details: str = ..., 
                progress_status: int = ..., 
                upgrade_state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterEvent(FabricEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_health_states = ..., 
                health_events = ..., 
                health_statistics = ..., 
                node_health_states = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterHealthChunk(Model):

        def __init__(
                self, 
                *, 
                application_health_state_chunks = ..., 
                health_state = ..., 
                node_health_state_chunks = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterHealthChunkQueryDescription(Model):

        def __init__(
                self, 
                *, 
                application_filters = ..., 
                application_health_policies = ..., 
                cluster_health_policy = ..., 
                node_filters = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterHealthPolicies(Model):

        def __init__(
                self, 
                *, 
                application_health_policy_map = ..., 
                cluster_health_policy = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterHealthPolicy(Model):

        def __init__(
                self, 
                *, 
                application_type_health_policy_map = ..., 
                consider_warning_as_error: bool = False, 
                max_percent_unhealthy_applications: int = 0, 
                max_percent_unhealthy_nodes: int = 0, 
                node_type_health_policy_map = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterHealthReportExpiredEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterLoadInfo(Model):

        def __init__(
                self, 
                *, 
                last_balancing_end_time_utc = ..., 
                last_balancing_start_time_utc = ..., 
                load_metric_information = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterManifest(Model):

        def __init__(
                self, 
                *, 
                manifest: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterNewHealthReportEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeCompletedEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                overall_upgrade_elapsed_time_in_ms: float, 
                target_cluster_version: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeDescriptionObject(Model):

        def __init__(
                self, 
                *, 
                application_health_policy_map = ..., 
                cluster_health_policy = ..., 
                cluster_upgrade_health_policy = ..., 
                code_version: str = ..., 
                config_version: str = ..., 
                enable_delta_health_evaluation: bool = ..., 
                force_restart: bool = ..., 
                monitoring_policy = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                sort_order = "Default", 
                upgrade_kind = "Rolling", 
                upgrade_replica_set_check_timeout_in_seconds: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeDomainCompletedEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                target_cluster_version: str, 
                time_stamp, 
                upgrade_domain_elapsed_time_in_ms: float, 
                upgrade_domains: str, 
                upgrade_state: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeHealthPolicyObject(Model):

        def __init__(
                self, 
                *, 
                max_percent_delta_unhealthy_nodes: int = ..., 
                max_percent_upgrade_domain_delta_unhealthy_nodes: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeProgressObject(Model):

        def __init__(
                self, 
                *, 
                code_version: str = ..., 
                config_version: str = ..., 
                current_upgrade_domain_progress = ..., 
                current_upgrade_units_progress = ..., 
                failure_reason = ..., 
                failure_timestamp_utc: str = ..., 
                is_node_by_node: bool = False, 
                next_upgrade_domain: str = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                start_timestamp_utc: str = ..., 
                unhealthy_evaluations = ..., 
                upgrade_description = ..., 
                upgrade_domain_duration_in_milliseconds: str = ..., 
                upgrade_domain_progress_at_failure = ..., 
                upgrade_domains = ..., 
                upgrade_duration_in_milliseconds: str = ..., 
                upgrade_state = ..., 
                upgrade_units = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeRollbackCompletedEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                failure_reason: str, 
                has_correlated_events: bool = ..., 
                overall_upgrade_elapsed_time_in_ms: float, 
                target_cluster_version: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeRollbackStartedEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                failure_reason: str, 
                has_correlated_events: bool = ..., 
                overall_upgrade_elapsed_time_in_ms: float, 
                target_cluster_version: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterUpgradeStartedEvent(ClusterEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                current_cluster_version: str, 
                event_instance_id: str, 
                failure_action: str, 
                has_correlated_events: bool = ..., 
                rolling_upgrade_mode: str, 
                target_cluster_version: str, 
                time_stamp, 
                upgrade_type: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ClusterVersion(Model):

        def __init__(
                self, 
                *, 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CodePackageEntryPoint(Model):

        def __init__(
                self, 
                *, 
                code_package_entry_point_statistics = ..., 
                entry_point_location: str = ..., 
                instance_id: str = ..., 
                next_activation_time = ..., 
                process_id: str = ..., 
                run_as_user_name: str = ..., 
                status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CodePackageEntryPointStatistics(Model):

        def __init__(
                self, 
                *, 
                activation_count: str = ..., 
                activation_failure_count: str = ..., 
                continuous_activation_failure_count: str = ..., 
                continuous_exit_failure_count: str = ..., 
                exit_count: str = ..., 
                exit_failure_count: str = ..., 
                last_activation_time = ..., 
                last_exit_code: str = ..., 
                last_exit_time = ..., 
                last_successful_activation_time = ..., 
                last_successful_exit_time = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ComposeDeploymentStatus(str, Enum):
        creating = "Creating"
        deleting = "Deleting"
        failed = "Failed"
        invalid = "Invalid"
        provisioning = "Provisioning"
        ready = "Ready"
        unprovisioning = "Unprovisioning"
        upgrading = "Upgrading"


    class azure.servicefabric.models.ComposeDeploymentStatusInfo(Model):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                name: str = ..., 
                status = ..., 
                status_details: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ComposeDeploymentUpgradeDescription(Model):

        def __init__(
                self, 
                *, 
                application_health_policy = ..., 
                compose_file_content: str, 
                deployment_name: str, 
                force_restart: bool = ..., 
                monitoring_policy = ..., 
                registry_credential = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                upgrade_kind = "Rolling", 
                upgrade_replica_set_check_timeout_in_seconds: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ComposeDeploymentUpgradeProgressInfo(Model):

        def __init__(
                self, 
                *, 
                application_health_policy = ..., 
                application_name: str = ..., 
                application_unhealthy_evaluations = ..., 
                application_upgrade_status_details: str = ..., 
                current_upgrade_domain_duration: str = ..., 
                current_upgrade_domain_progress = ..., 
                deployment_name: str = ..., 
                failure_reason = ..., 
                failure_timestamp_utc: str = ..., 
                force_restart: bool = ..., 
                monitoring_policy = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                start_timestamp_utc: str = ..., 
                target_application_type_version: str = ..., 
                upgrade_domain_progress_at_failure = ..., 
                upgrade_duration: str = ..., 
                upgrade_kind = "Rolling", 
                upgrade_replica_set_check_timeout_in_seconds: int = ..., 
                upgrade_state = ..., 
                upgrade_status_details: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ComposeDeploymentUpgradeState(str, Enum):
        failed = "Failed"
        invalid = "Invalid"
        provisioning_target = "ProvisioningTarget"
        rolling_back_completed = "RollingBackCompleted"
        rolling_back_in_progress = "RollingBackInProgress"
        rolling_forward_completed = "RollingForwardCompleted"
        rolling_forward_in_progress = "RollingForwardInProgress"
        rolling_forward_pending = "RollingForwardPending"
        unprovisioning_current = "UnprovisioningCurrent"
        unprovisioning_target = "UnprovisioningTarget"


    class azure.servicefabric.models.ConfigParameterOverride(Model):

        def __init__(
                self, 
                *, 
                parameter_name: str, 
                parameter_value: str, 
                persist_across_upgrade: bool = ..., 
                section_name: str, 
                timeout = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerApiRequestBody(Model):

        def __init__(
                self, 
                *, 
                body: str = ..., 
                content_type: str = ..., 
                http_verb: str = ..., 
                uri_path: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerApiResponse(Model):

        def __init__(
                self, 
                *, 
                container_api_result, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerApiResult(Model):

        def __init__(
                self, 
                *, 
                body: str = ..., 
                content_encoding: str = ..., 
                content_type: str = ..., 
                status: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerCodePackageProperties(Model):
        instance_view: ContainerInstanceView

        def __init__(
                self, 
                *, 
                commands = ..., 
                diagnostics = ..., 
                endpoints = ..., 
                entry_point: str = ..., 
                environment_variables = ..., 
                image: str, 
                image_registry_credential = ..., 
                labels = ..., 
                liveness_probe = ..., 
                name: str, 
                readiness_probe = ..., 
                reliable_collections_refs = ..., 
                resources, 
                settings = ..., 
                volume_refs = ..., 
                volumes = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerEvent(Model):

        def __init__(
                self, 
                *, 
                count: int = ..., 
                first_timestamp: str = ..., 
                last_timestamp: str = ..., 
                message: str = ..., 
                name: str = ..., 
                type: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerInstanceEvent(FabricEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerInstanceView(Model):

        def __init__(
                self, 
                *, 
                current_state = ..., 
                events = ..., 
                previous_state = ..., 
                restart_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerLabel(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                value: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerLogs(Model):

        def __init__(
                self, 
                *, 
                content: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ContainerState(Model):

        def __init__(
                self, 
                *, 
                detail_status: str = ..., 
                exit_code: str = ..., 
                finish_time = ..., 
                start_time = ..., 
                state: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CreateComposeDeploymentDescription(Model):

        def __init__(
                self, 
                *, 
                compose_file_content: str, 
                deployment_name: str, 
                registry_credential = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CreateFabricDump(str, Enum):
        false = "False"
        true = "True"


    class azure.servicefabric.models.CurrentUpgradeDomainProgressInfo(Model):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                node_upgrade_progress_list = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.CurrentUpgradeUnitsProgressInfo(Model):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                node_upgrade_progress_list = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DataLossMode(str, Enum):
        full_data_loss = "FullDataLoss"
        invalid = "Invalid"
        partial_data_loss = "PartialDataLoss"


    class azure.servicefabric.models.DayOfWeek(str, Enum):
        friday = "Friday"
        monday = "Monday"
        saturday = "Saturday"
        sunday = "Sunday"
        thursday = "Thursday"
        tuesday = "Tuesday"
        wednesday = "Wednesday"


    class azure.servicefabric.models.DeactivationIntent(str, Enum):
        pause = "Pause"
        remove_data = "RemoveData"
        restart = "Restart"


    class azure.servicefabric.models.DeactivationIntentDescription(Model):

        def __init__(
                self, 
                *, 
                deactivation_intent = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DefaultExecutionPolicy(ExecutionPolicy):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.DeletePropertyBatchOperation(PropertyBatchOperation):

        def __init__(
                self, 
                *, 
                property_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeltaNodesCheckHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                baseline_error_count: int = ..., 
                baseline_total_count: int = ..., 
                description: str = ..., 
                max_percent_delta_unhealthy_nodes: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployServicePackageToNodeDescription(Model):

        def __init__(
                self, 
                *, 
                application_type_name: str, 
                application_type_version: str, 
                node_name: str, 
                package_sharing_policy = ..., 
                service_manifest_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                deployed_service_package_health_states = ..., 
                health_events = ..., 
                health_statistics = ..., 
                name: str = ..., 
                node_name: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_name: str = ..., 
                description: str = ..., 
                node_name: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationHealthReportExpiredEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_instance_id: int, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                node_name: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationHealthState(EntityHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_name: str = ..., 
                node_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationHealthStateChunk(EntityHealthStateChunk):

        def __init__(
                self, 
                *, 
                deployed_service_package_health_state_chunks = ..., 
                health_state = ..., 
                node_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationHealthStateChunkList(Model):

        def __init__(
                self, 
                *, 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationHealthStateFilter(Model):

        def __init__(
                self, 
                *, 
                deployed_service_package_filters = ..., 
                health_state_filter: int = 0, 
                node_name_filter: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationInfo(Model):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                id: str = ..., 
                log_directory: str = ..., 
                name: str = ..., 
                status = ..., 
                temp_directory: str = ..., 
                type_name: str = ..., 
                type_version: str = ..., 
                work_directory: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationNewHealthReportEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                application_instance_id: int, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                node_name: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedApplicationStatus(str, Enum):
        activating = "Activating"
        active = "Active"
        deactivating = "Deactivating"
        downloading = "Downloading"
        invalid = "Invalid"
        upgrading = "Upgrading"


    class azure.servicefabric.models.DeployedApplicationsHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_deployed_applications: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedCodePackageInfo(Model):

        def __init__(
                self, 
                *, 
                host_isolation_mode = ..., 
                host_type = ..., 
                main_entry_point = ..., 
                name: str = ..., 
                run_frequency_interval: str = ..., 
                service_manifest_name: str = ..., 
                service_package_activation_id: str = ..., 
                setup_entry_point = ..., 
                status = ..., 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_name: str = ..., 
                health_events = ..., 
                health_statistics = ..., 
                node_name: str = ..., 
                service_manifest_name: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_name: str = ..., 
                description: str = ..., 
                node_name: str = ..., 
                service_manifest_name: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageHealthReportExpiredEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                node_name: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                service_manifest: str, 
                service_package_activation_id: str, 
                service_package_instance_id: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageHealthState(EntityHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                application_name: str = ..., 
                node_name: str = ..., 
                service_manifest_name: str = ..., 
                service_package_activation_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageHealthStateChunk(EntityHealthStateChunk):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                service_manifest_name: str = ..., 
                service_package_activation_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageHealthStateChunkList(Model):

        def __init__(
                self, 
                *, 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageHealthStateFilter(Model):

        def __init__(
                self, 
                *, 
                health_state_filter: int = 0, 
                service_manifest_name_filter: str = ..., 
                service_package_activation_id_filter: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageInfo(Model):

        def __init__(
                self, 
                *, 
                name: str = ..., 
                service_package_activation_id: str = ..., 
                status = ..., 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackageNewHealthReportEvent(ApplicationEvent):

        def __init__(
                self, 
                *, 
                application_id: str, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                node_name: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                service_manifest_name: str, 
                service_package_activation_id: str, 
                service_package_instance_id: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServicePackagesHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServiceReplicaDetailInfo(Model):

        def __init__(
                self, 
                *, 
                current_service_operation = ..., 
                current_service_operation_start_time_utc = ..., 
                partition_id: str = ..., 
                reported_load = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServiceReplicaInfo(Model):

        def __init__(
                self, 
                *, 
                address: str = ..., 
                code_package_name: str = ..., 
                host_process_id: str = ..., 
                partition_id: str = ..., 
                replica_status = ..., 
                service_manifest_name: str = ..., 
                service_name: str = ..., 
                service_package_activation_id: str = ..., 
                service_type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedServiceTypeInfo(Model):

        def __init__(
                self, 
                *, 
                code_package_name: str = ..., 
                service_manifest_name: str = ..., 
                service_package_activation_id: str = ..., 
                service_type_name: str = ..., 
                status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedStatefulServiceReplicaDetailInfo(DeployedServiceReplicaDetailInfo):

        def __init__(
                self, 
                *, 
                current_replicator_operation = ..., 
                current_service_operation = ..., 
                current_service_operation_start_time_utc = ..., 
                deployed_service_replica_query_result = ..., 
                partition_id: str = ..., 
                read_status = ..., 
                replica_id: str = ..., 
                replica_status = ..., 
                replicator_status = ..., 
                reported_load = ..., 
                service_name: str = ..., 
                write_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedStatefulServiceReplicaInfo(DeployedServiceReplicaInfo):

        def __init__(
                self, 
                *, 
                address: str = ..., 
                code_package_name: str = ..., 
                host_process_id: str = ..., 
                partition_id: str = ..., 
                reconfiguration_information = ..., 
                replica_id: str = ..., 
                replica_role = ..., 
                replica_status = ..., 
                service_manifest_name: str = ..., 
                service_name: str = ..., 
                service_package_activation_id: str = ..., 
                service_type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedStatelessServiceInstanceDetailInfo(DeployedServiceReplicaDetailInfo):

        def __init__(
                self, 
                *, 
                current_service_operation = ..., 
                current_service_operation_start_time_utc = ..., 
                deployed_service_replica_query_result = ..., 
                instance_id: str = ..., 
                partition_id: str = ..., 
                reported_load = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeployedStatelessServiceInstanceInfo(DeployedServiceReplicaInfo):

        def __init__(
                self, 
                *, 
                address: str = ..., 
                code_package_name: str = ..., 
                host_process_id: str = ..., 
                instance_id: str = ..., 
                partition_id: str = ..., 
                replica_status = ..., 
                service_manifest_name: str = ..., 
                service_name: str = ..., 
                service_package_activation_id: str = ..., 
                service_type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DeploymentStatus(str, Enum):
        activating = "Activating"
        active = "Active"
        deactivating = "Deactivating"
        downloading = "Downloading"
        failed = "Failed"
        invalid = "Invalid"
        ran_to_completion = "RanToCompletion"
        upgrading = "Upgrading"


    class azure.servicefabric.models.DiagnosticsDescription(Model):

        def __init__(
                self, 
                *, 
                default_sink_refs = ..., 
                enabled: bool = ..., 
                sinks = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DiagnosticsRef(Model):

        def __init__(
                self, 
                *, 
                enabled: bool = ..., 
                sink_refs = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DiagnosticsSinkKind(str, Enum):
        azure_internal_monitoring_pipeline = "AzureInternalMonitoringPipeline"
        invalid = "Invalid"


    class azure.servicefabric.models.DiagnosticsSinkProperties(Model):

        def __init__(
                self, 
                *, 
                description: str = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DisableBackupDescription(Model):

        def __init__(
                self, 
                *, 
                clean_backup: bool, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DiskInfo(Model):

        def __init__(
                self, 
                *, 
                available_space: str = ..., 
                capacity: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DoublePropertyValue(PropertyValue):

        def __init__(
                self, 
                *, 
                data: float, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.DsmsAzureBlobBackupStorageDescription(BackupStorageDescription):

        def __init__(
                self, 
                *, 
                container_name: str, 
                friendly_name: str = ..., 
                storage_credentials_source_location: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EnableBackupDescription(Model):

        def __init__(
                self, 
                *, 
                backup_policy_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EndpointProperties(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                port: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EndpointRef(Model):

        def __init__(
                self, 
                *, 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EnsureAvailabilitySafetyCheck(PartitionSafetyCheck):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EnsurePartitionQuorumSafetyCheck(PartitionSafetyCheck):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EntityHealth(Model):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                health_events = ..., 
                health_statistics = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EntityHealthState(Model):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EntityHealthStateChunk(Model):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EntityHealthStateChunkList(Model):

        def __init__(
                self, 
                *, 
                total_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EntityKind(str, Enum):
        application = "Application"
        cluster = "Cluster"
        deployed_application = "DeployedApplication"
        deployed_service_package = "DeployedServicePackage"
        invalid = "Invalid"
        node = "Node"
        partition = "Partition"
        replica = "Replica"
        service = "Service"


    class azure.servicefabric.models.EntityKindHealthStateCount(Model):

        def __init__(
                self, 
                *, 
                entity_kind = ..., 
                health_state_count = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EntryPointStatus(str, Enum):
        invalid = "Invalid"
        pending = "Pending"
        started = "Started"
        starting = "Starting"
        stopped = "Stopped"
        stopping = "Stopping"


    class azure.servicefabric.models.EnvironmentVariable(Model):

        def __init__(
                self, 
                *, 
                name: str = ..., 
                type = "ClearText", 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EnvironmentVariableType(str, Enum):
        clear_text = "ClearText"
        key_vault_reference = "KeyVaultReference"
        secret_value_reference = "SecretValueReference"


    class azure.servicefabric.models.Epoch(Model):

        def __init__(
                self, 
                *, 
                configuration_version: str = ..., 
                data_loss_version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.EventHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                consider_warning_as_error: bool = ..., 
                description: str = ..., 
                unhealthy_event = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ExecutingFaultsChaosEvent(ChaosEvent):

        def __init__(
                self, 
                *, 
                faults = ..., 
                time_stamp_utc, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ExecutionPolicy(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.ExecutionPolicyType(str, Enum):
        default = "Default"
        run_to_completion = "RunToCompletion"


    class azure.servicefabric.models.ExternalStoreProvisionApplicationTypeDescription(ProvisionApplicationTypeDescriptionBase):

        def __init__(
                self, 
                *, 
                application_package_download_uri: str, 
                application_type_name: str, 
                application_type_version: str, 
                async_property: bool, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FabricCodeVersionInfo(Model):

        def __init__(
                self, 
                *, 
                code_version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FabricConfigVersionInfo(Model):

        def __init__(
                self, 
                *, 
                config_version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FabricError(Model):

        def __init__(
                self, 
                *, 
                error, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FabricErrorCodes(str, Enum):
        e_abort = "E_ABORT"
        e_fail = "E_FAIL"
        e_invalidarg = "E_INVALIDARG"
        fabric_e_application_already_exists = "FABRIC_E_APPLICATION_ALREADY_EXISTS"
        fabric_e_application_already_in_target_version = "FABRIC_E_APPLICATION_ALREADY_IN_TARGET_VERSION"
        fabric_e_application_not_found = "FABRIC_E_APPLICATION_NOT_FOUND"
        fabric_e_application_not_upgrading = "FABRIC_E_APPLICATION_NOT_UPGRADING"
        fabric_e_application_type_already_exists = "FABRIC_E_APPLICATION_TYPE_ALREADY_EXISTS"
        fabric_e_application_type_in_use = "FABRIC_E_APPLICATION_TYPE_IN_USE"
        fabric_e_application_type_not_found = "FABRIC_E_APPLICATION_TYPE_NOT_FOUND"
        fabric_e_application_type_provision_in_progress = "FABRIC_E_APPLICATION_TYPE_PROVISION_IN_PROGRESS"
        fabric_e_application_upgrade_in_progress = "FABRIC_E_APPLICATION_UPGRADE_IN_PROGRESS"
        fabric_e_application_upgrade_validation_error = "FABRIC_E_APPLICATION_UPGRADE_VALIDATION_ERROR"
        fabric_e_backup_in_progress = "FABRIC_E_BACKUP_IN_PROGRESS"
        fabric_e_backup_is_enabled = "FABRIC_E_BACKUP_IS_ENABLED"
        fabric_e_backup_not_enabled = "FABRIC_E_BACKUP_NOT_ENABLED"
        fabric_e_backup_policy_already_existing = "FABRIC_E_BACKUP_POLICY_ALREADY_EXISTING"
        fabric_e_backup_policy_not_existing = "FABRIC_E_BACKUP_POLICY_NOT_EXISTING"
        fabric_e_communication_error = "FABRIC_E_COMMUNICATION_ERROR"
        fabric_e_configuration_parameter_not_found = "FABRIC_E_CONFIGURATION_PARAMETER_NOT_FOUND"
        fabric_e_configuration_section_not_found = "FABRIC_E_CONFIGURATION_SECTION_NOT_FOUND"
        fabric_e_directory_not_found = "FABRIC_E_DIRECTORY_NOT_FOUND"
        fabric_e_enumeration_completed = "FABRIC_E_ENUMERATION_COMPLETED"
        fabric_e_fabric_already_in_target_version = "FABRIC_E_FABRIC_ALREADY_IN_TARGET_VERSION"
        fabric_e_fabric_not_upgrading = "FABRIC_E_FABRIC_NOT_UPGRADING"
        fabric_e_fabric_upgrade_in_progress = "FABRIC_E_FABRIC_UPGRADE_IN_PROGRESS"
        fabric_e_fabric_upgrade_validation_error = "FABRIC_E_FABRIC_UPGRADE_VALIDATION_ERROR"
        fabric_e_fabric_version_already_exists = "FABRIC_E_FABRIC_VERSION_ALREADY_EXISTS"
        fabric_e_fabric_version_in_use = "FABRIC_E_FABRIC_VERSION_IN_USE"
        fabric_e_fabric_version_not_found = "FABRIC_E_FABRIC_VERSION_NOT_FOUND"
        fabric_e_fault_analysis_service_not_existing = "FABRIC_E_FAULT_ANALYSIS_SERVICE_NOT_EXISTING"
        fabric_e_file_not_found = "FABRIC_E_FILE_NOT_FOUND"
        fabric_e_health_entity_not_found = "FABRIC_E_HEALTH_ENTITY_NOT_FOUND"
        fabric_e_health_stale_report = "FABRIC_E_HEALTH_STALE_REPORT"
        fabric_e_imagebuilder_reserved_directory_error = "FABRIC_E_IMAGEBUILDER_RESERVED_DIRECTORY_ERROR"
        fabric_e_imagebuilder_validation_error = "FABRIC_E_IMAGEBUILDER_VALIDATION_ERROR"
        fabric_e_instance_id_mismatch = "FABRIC_E_INSTANCE_ID_MISMATCH"
        fabric_e_invalid_address = "FABRIC_E_INVALID_ADDRESS"
        fabric_e_invalid_atomic_group = "FABRIC_E_INVALID_ATOMIC_GROUP"
        fabric_e_invalid_configuration = "FABRIC_E_INVALID_CONFIGURATION"
        fabric_e_invalid_for_stateless_services = "FABRIC_E_INVALID_FOR_STATELESS_SERVICES"
        fabric_e_invalid_name_uri = "FABRIC_E_INVALID_NAME_URI"
        fabric_e_invalid_partition_key = "FABRIC_E_INVALID_PARTITION_KEY"
        fabric_e_invalid_service_scaling_policy = "FABRIC_E_INVALID_SERVICE_SCALING_POLICY"
        fabric_e_key_not_found = "FABRIC_E_KEY_NOT_FOUND"
        fabric_e_key_too_large = "FABRIC_E_KEY_TOO_LARGE"
        fabric_e_name_already_exists = "FABRIC_E_NAME_ALREADY_EXISTS"
        fabric_e_name_does_not_exist = "FABRIC_E_NAME_DOES_NOT_EXIST"
        fabric_e_name_not_empty = "FABRIC_E_NAME_NOT_EMPTY"
        fabric_e_no_write_quorum = "FABRIC_E_NO_WRITE_QUORUM"
        fabric_e_node_has_not_stopped_yet = "FABRIC_E_NODE_HAS_NOT_STOPPED_YET"
        fabric_e_node_is_up = "FABRIC_E_NODE_IS_UP"
        fabric_e_node_not_found = "FABRIC_E_NODE_NOT_FOUND"
        fabric_e_not_primary = "FABRIC_E_NOT_PRIMARY"
        fabric_e_not_ready = "FABRIC_E_NOT_READY"
        fabric_e_operation_not_complete = "FABRIC_E_OPERATION_NOT_COMPLETE"
        fabric_e_partition_not_found = "FABRIC_E_PARTITION_NOT_FOUND"
        fabric_e_path_too_long = "FABRIC_E_PATH_TOO_LONG"
        fabric_e_property_check_failed = "FABRIC_E_PROPERTY_CHECK_FAILED"
        fabric_e_property_does_not_exist = "FABRIC_E_PROPERTY_DOES_NOT_EXIST"
        fabric_e_reconfiguration_pending = "FABRIC_E_RECONFIGURATION_PENDING"
        fabric_e_replica_does_not_exist = "FABRIC_E_REPLICA_DOES_NOT_EXIST"
        fabric_e_restore_in_progress = "FABRIC_E_RESTORE_IN_PROGRESS"
        fabric_e_restore_source_target_partition_mismatch = "FABRIC_E_RESTORE_SOURCE_TARGET_PARTITION_MISMATCH"
        fabric_e_sequence_number_check_failed = "FABRIC_E_SEQUENCE_NUMBER_CHECK_FAILED"
        fabric_e_service_affinity_chain_not_supported = "FABRIC_E_SERVICE_AFFINITY_CHAIN_NOT_SUPPORTED"
        fabric_e_service_already_exists = "FABRIC_E_SERVICE_ALREADY_EXISTS"
        fabric_e_service_does_not_exist = "FABRIC_E_SERVICE_DOES_NOT_EXIST"
        fabric_e_service_group_already_exists = "FABRIC_E_SERVICE_GROUP_ALREADY_EXISTS"
        fabric_e_service_group_does_not_exist = "FABRIC_E_SERVICE_GROUP_DOES_NOT_EXIST"
        fabric_e_service_manifest_not_found = "FABRIC_E_SERVICE_MANIFEST_NOT_FOUND"
        fabric_e_service_metadata_mismatch = "FABRIC_E_SERVICE_METADATA_MISMATCH"
        fabric_e_service_offline = "FABRIC_E_SERVICE_OFFLINE"
        fabric_e_service_type_mismatch = "FABRIC_E_SERVICE_TYPE_MISMATCH"
        fabric_e_service_type_not_found = "FABRIC_E_SERVICE_TYPE_NOT_FOUND"
        fabric_e_service_type_template_not_found = "FABRIC_E_SERVICE_TYPE_TEMPLATE_NOT_FOUND"
        fabric_e_single_instance_application_already_exists = "FABRIC_E_SINGLE_INSTANCE_APPLICATION_ALREADY_EXISTS"
        fabric_e_single_instance_application_not_found = "FABRIC_E_SINGLE_INSTANCE_APPLICATION_NOT_FOUND"
        fabric_e_timeout = "FABRIC_E_TIMEOUT"
        fabric_e_value_empty = "FABRIC_E_VALUE_EMPTY"
        fabric_e_value_too_large = "FABRIC_E_VALUE_TOO_LARGE"
        fabric_e_volume_already_exists = "FABRIC_E_VOLUME_ALREADY_EXISTS"
        fabric_e_volume_not_found = "FABRIC_E_VOLUME_NOT_FOUND"
        serialization_error = "SerializationError"


    class azure.servicefabric.models.FabricErrorError(Model):

        def __init__(
                self, 
                *, 
                code, 
                message: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FabricErrorException(HttpOperationError):

        def __init__(
                self, 
                deserialize, 
                response, 
                *args
            ): ...


    class azure.servicefabric.models.FabricEvent(Model):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FabricEventKind(str, Enum):
        application_container_instance_exited = "ApplicationContainerInstanceExited"
        application_created = "ApplicationCreated"
        application_deleted = "ApplicationDeleted"
        application_event = "ApplicationEvent"
        application_health_report_expired = "ApplicationHealthReportExpired"
        application_new_health_report = "ApplicationNewHealthReport"
        application_process_exited = "ApplicationProcessExited"
        application_upgrade_completed = "ApplicationUpgradeCompleted"
        application_upgrade_domain_completed = "ApplicationUpgradeDomainCompleted"
        application_upgrade_rollback_completed = "ApplicationUpgradeRollbackCompleted"
        application_upgrade_rollback_started = "ApplicationUpgradeRollbackStarted"
        application_upgrade_started = "ApplicationUpgradeStarted"
        chaos_code_package_restart_scheduled = "ChaosCodePackageRestartScheduled"
        chaos_node_restart_scheduled = "ChaosNodeRestartScheduled"
        chaos_partition_primary_move_scheduled = "ChaosPartitionPrimaryMoveScheduled"
        chaos_partition_secondary_move_scheduled = "ChaosPartitionSecondaryMoveScheduled"
        chaos_replica_removal_scheduled = "ChaosReplicaRemovalScheduled"
        chaos_replica_restart_scheduled = "ChaosReplicaRestartScheduled"
        chaos_started = "ChaosStarted"
        chaos_stopped = "ChaosStopped"
        cluster_event = "ClusterEvent"
        cluster_health_report_expired = "ClusterHealthReportExpired"
        cluster_new_health_report = "ClusterNewHealthReport"
        cluster_upgrade_completed = "ClusterUpgradeCompleted"
        cluster_upgrade_domain_completed = "ClusterUpgradeDomainCompleted"
        cluster_upgrade_rollback_completed = "ClusterUpgradeRollbackCompleted"
        cluster_upgrade_rollback_started = "ClusterUpgradeRollbackStarted"
        cluster_upgrade_started = "ClusterUpgradeStarted"
        container_instance_event = "ContainerInstanceEvent"
        deployed_application_health_report_expired = "DeployedApplicationHealthReportExpired"
        deployed_application_new_health_report = "DeployedApplicationNewHealthReport"
        deployed_service_package_health_report_expired = "DeployedServicePackageHealthReportExpired"
        deployed_service_package_new_health_report = "DeployedServicePackageNewHealthReport"
        node_aborted = "NodeAborted"
        node_added_to_cluster = "NodeAddedToCluster"
        node_closed = "NodeClosed"
        node_deactivate_completed = "NodeDeactivateCompleted"
        node_deactivate_started = "NodeDeactivateStarted"
        node_down = "NodeDown"
        node_event = "NodeEvent"
        node_health_report_expired = "NodeHealthReportExpired"
        node_new_health_report = "NodeNewHealthReport"
        node_open_failed = "NodeOpenFailed"
        node_open_succeeded = "NodeOpenSucceeded"
        node_removed_from_cluster = "NodeRemovedFromCluster"
        node_up = "NodeUp"
        partition_analysis_event = "PartitionAnalysisEvent"
        partition_event = "PartitionEvent"
        partition_health_report_expired = "PartitionHealthReportExpired"
        partition_new_health_report = "PartitionNewHealthReport"
        partition_primary_move_analysis = "PartitionPrimaryMoveAnalysis"
        partition_reconfigured = "PartitionReconfigured"
        replica_event = "ReplicaEvent"
        service_created = "ServiceCreated"
        service_deleted = "ServiceDeleted"
        service_event = "ServiceEvent"
        service_health_report_expired = "ServiceHealthReportExpired"
        service_new_health_report = "ServiceNewHealthReport"
        stateful_replica_health_report_expired = "StatefulReplicaHealthReportExpired"
        stateful_replica_new_health_report = "StatefulReplicaNewHealthReport"
        stateless_replica_health_report_expired = "StatelessReplicaHealthReportExpired"
        stateless_replica_new_health_report = "StatelessReplicaNewHealthReport"


    class azure.servicefabric.models.FabricReplicaStatus(str, Enum):
        down = "Down"
        invalid = "Invalid"
        up = "Up"


    class azure.servicefabric.models.FailedPropertyBatchInfo(PropertyBatchInfo):

        def __init__(
                self, 
                *, 
                error_message: str = ..., 
                operation_index: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FailedUpgradeDomainProgressObject(Model):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                node_upgrade_progress_list = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FailureAction(str, Enum):
        invalid = "Invalid"
        manual = "Manual"
        rollback = "Rollback"


    class azure.servicefabric.models.FailureReason(str, Enum):
        health_check = "HealthCheck"
        interrupted = "Interrupted"
        none = "None"
        overall_upgrade_timeout = "OverallUpgradeTimeout"
        upgrade_domain_timeout = "UpgradeDomainTimeout"


    class azure.servicefabric.models.FailureUpgradeDomainProgressInfo(Model):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                node_upgrade_progress_list = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FileInfo(Model):

        def __init__(
                self, 
                *, 
                file_size: str = ..., 
                file_version = ..., 
                modified_date = ..., 
                store_relative_path: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FileShareBackupStorageDescription(BackupStorageDescription):

        def __init__(
                self, 
                *, 
                friendly_name: str = ..., 
                path: str, 
                primary_password: str = ..., 
                primary_user_name: str = ..., 
                secondary_password: str = ..., 
                secondary_user_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FileVersion(Model):

        def __init__(
                self, 
                *, 
                epoch_configuration_number: str = ..., 
                epoch_data_loss_number: str = ..., 
                version_number: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FolderInfo(Model):

        def __init__(
                self, 
                *, 
                file_count: str = ..., 
                store_relative_path: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FolderSizeInfo(Model):

        def __init__(
                self, 
                *, 
                folder_size: str = ..., 
                store_relative_path: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.FrequencyBasedBackupScheduleDescription(BackupScheduleDescription):

        def __init__(
                self, 
                *, 
                interval, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.GatewayDestination(Model):

        def __init__(
                self, 
                *, 
                application_name: str, 
                endpoint_name: str, 
                service_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.GatewayResourceDescription(Model):
        ip_address: str
        status: Union[str, ResourceStatus]
        status_details: str

        def __init__(
                self, 
                *, 
                description: str = ..., 
                destination_network, 
                http = ..., 
                name: str, 
                source_network, 
                tcp = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.GetBackupByStorageQueryDescription(Model):

        def __init__(
                self, 
                *, 
                backup_entity, 
                end_date_time_filter = ..., 
                latest: bool = False, 
                start_date_time_filter = ..., 
                storage, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.GetPropertyBatchOperation(PropertyBatchOperation):

        def __init__(
                self, 
                *, 
                include_value: bool = False, 
                property_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.GuidPropertyValue(PropertyValue):

        def __init__(
                self, 
                *, 
                data: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HeaderMatchType(str, Enum):
        exact = "exact"


    class azure.servicefabric.models.HealthEvaluation(Model):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HealthEvaluationKind(str, Enum):
        application = "Application"
        application_type_applications = "ApplicationTypeApplications"
        applications = "Applications"
        delta_nodes_check = "DeltaNodesCheck"
        deployed_application = "DeployedApplication"
        deployed_applications = "DeployedApplications"
        deployed_service_package = "DeployedServicePackage"
        deployed_service_packages = "DeployedServicePackages"
        event = "Event"
        invalid = "Invalid"
        node = "Node"
        node_type_nodes = "NodeTypeNodes"
        nodes = "Nodes"
        partition = "Partition"
        partitions = "Partitions"
        replica = "Replica"
        replicas = "Replicas"
        service = "Service"
        services = "Services"
        system_application = "SystemApplication"
        upgrade_domain_delta_nodes_check = "UpgradeDomainDeltaNodesCheck"
        upgrade_domain_deployed_applications = "UpgradeDomainDeployedApplications"
        upgrade_domain_nodes = "UpgradeDomainNodes"


    class azure.servicefabric.models.HealthEvaluationWrapper(Model):

        def __init__(
                self, 
                *, 
                health_evaluation = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HealthEvent(HealthInformation):

        def __init__(
                self, 
                *, 
                description: str = ..., 
                health_report_id: str = ..., 
                health_state, 
                is_expired: bool = ..., 
                last_error_transition_at = ..., 
                last_modified_utc_timestamp = ..., 
                last_ok_transition_at = ..., 
                last_warning_transition_at = ..., 
                property: str, 
                remove_when_expired: bool = ..., 
                sequence_number: str = ..., 
                source_id: str, 
                source_utc_timestamp = ..., 
                time_to_live_in_milli_seconds = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HealthInformation(Model):

        def __init__(
                self, 
                *, 
                description: str = ..., 
                health_report_id: str = ..., 
                health_state, 
                property: str, 
                remove_when_expired: bool = ..., 
                sequence_number: str = ..., 
                source_id: str, 
                time_to_live_in_milli_seconds = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HealthState(str, Enum):
        error = "Error"
        invalid = "Invalid"
        ok = "Ok"
        unknown = "Unknown"
        warning = "Warning"


    class azure.servicefabric.models.HealthStateCount(Model):

        def __init__(
                self, 
                *, 
                error_count: int = ..., 
                ok_count: int = ..., 
                warning_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HealthStatistics(Model):

        def __init__(
                self, 
                *, 
                health_state_count_list = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HostIsolationMode(str, Enum):
        hyper_v = "HyperV"
        none = "None"
        process = "Process"


    class azure.servicefabric.models.HostType(str, Enum):
        container_host = "ContainerHost"
        exe_host = "ExeHost"
        invalid = "Invalid"


    class azure.servicefabric.models.HttpConfig(Model):

        def __init__(
                self, 
                *, 
                hosts, 
                name: str, 
                port: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HttpHostConfig(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                routes, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HttpRouteConfig(Model):

        def __init__(
                self, 
                *, 
                destination, 
                match, 
                name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HttpRouteMatchHeader(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                type = ..., 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HttpRouteMatchPath(Model):
        type: str = "prefix"

        def __init__(
                self, 
                *, 
                rewrite: str = ..., 
                value: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.HttpRouteMatchRule(Model):

        def __init__(
                self, 
                *, 
                headers = ..., 
                path, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.IdentityDescription(Model):

        def __init__(
                self, 
                *, 
                principal_id: str = ..., 
                tenant_id: str = ..., 
                token_service_endpoint: str = ..., 
                type: str, 
                user_assigned_identities = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.IdentityItemDescription(Model):

        def __init__(
                self, 
                *, 
                client_id: str = ..., 
                principal_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ImageRegistryCredential(Model):

        def __init__(
                self, 
                *, 
                password: str = ..., 
                password_type = "ClearText", 
                server: str, 
                username: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ImageRegistryPasswordType(str, Enum):
        clear_text = "ClearText"
        key_vault_reference = "KeyVaultReference"
        secret_value_reference = "SecretValueReference"


    class azure.servicefabric.models.ImageStoreContent(Model):

        def __init__(
                self, 
                *, 
                store_files = ..., 
                store_folders = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ImageStoreCopyDescription(Model):

        def __init__(
                self, 
                *, 
                check_mark_file: bool = ..., 
                remote_destination: str, 
                remote_source: str, 
                skip_files = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ImageStoreInfo(Model):

        def __init__(
                self, 
                *, 
                disk_info = ..., 
                used_by_copy = ..., 
                used_by_metadata = ..., 
                used_by_register = ..., 
                used_by_staging = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ImpactLevel(str, Enum):
        invalid = "Invalid"
        none = "None"
        remove_data = "RemoveData"
        remove_node = "RemoveNode"
        restart = "Restart"


    class azure.servicefabric.models.InlinedValueSecretResourceProperties(SecretResourceProperties):
        status: Union[str, ResourceStatus]
        status_details: str

        def __init__(
                self, 
                *, 
                content_type: str = ..., 
                description: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.InstanceLifecycleDescription(Model):

        def __init__(
                self, 
                *, 
                restore_replica_location_after_upgrade: bool = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.Int64PropertyValue(PropertyValue):

        def __init__(
                self, 
                *, 
                data: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.Int64RangePartitionInformation(PartitionInformation):

        def __init__(
                self, 
                *, 
                high_key: str = ..., 
                id: str = ..., 
                low_key: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.InvokeDataLossResult(Model):

        def __init__(
                self, 
                *, 
                error_code: int = ..., 
                selected_partition = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.InvokeQuorumLossResult(Model):

        def __init__(
                self, 
                *, 
                error_code: int = ..., 
                selected_partition = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.KeyValueStoreReplicaStatus(ReplicaStatusBase):

        def __init__(
                self, 
                *, 
                copy_notification_current_key_filter: str = ..., 
                copy_notification_current_progress: str = ..., 
                database_logical_size_estimate: str = ..., 
                database_row_count_estimate: str = ..., 
                status_details: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.LoadMetricInformation(Model):

        def __init__(
                self, 
                *, 
                action: str = ..., 
                activity_threshold: str = ..., 
                balancing_threshold: str = ..., 
                buffered_cluster_capacity_remaining: str = ..., 
                cluster_buffered_capacity: str = ..., 
                cluster_capacity: str = ..., 
                cluster_capacity_remaining: str = ..., 
                cluster_load: str = ..., 
                cluster_remaining_buffered_capacity: str = ..., 
                cluster_remaining_capacity: str = ..., 
                current_cluster_load: str = ..., 
                deviation_after: str = ..., 
                deviation_before: str = ..., 
                is_balanced_after: bool = ..., 
                is_balanced_before: bool = ..., 
                is_cluster_capacity_violation: bool = ..., 
                max_node_load_node_id = ..., 
                max_node_load_value: str = ..., 
                maximum_node_load: str = ..., 
                min_node_load_node_id = ..., 
                min_node_load_value: str = ..., 
                minimum_node_load: str = ..., 
                name: str = ..., 
                node_buffer_percentage: str = ..., 
                planned_load_removal: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.LoadMetricReport(Model):

        def __init__(
                self, 
                *, 
                current_value: str = ..., 
                last_reported_utc = ..., 
                name: str = ..., 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.LoadMetricReportInfo(Model):

        def __init__(
                self, 
                *, 
                current_value: str = ..., 
                last_reported_utc = ..., 
                name: str = ..., 
                value: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.LoadedPartitionInformationQueryDescription(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                max_results: int = ..., 
                metric_name: str = ..., 
                ordering = "Desc", 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.LoadedPartitionInformationResult(Model):

        def __init__(
                self, 
                *, 
                load: int, 
                metric_name: str, 
                partition_id: str, 
                service_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.LoadedPartitionInformationResultList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.LocalNetworkResourceProperties(NetworkResourceProperties):
        status: Union[str, ResourceStatus]
        status_details: str

        def __init__(
                self, 
                *, 
                description: str = ..., 
                network_address_prefix: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ManagedApplicationIdentity(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                principal_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ManagedApplicationIdentityDescription(Model):

        def __init__(
                self, 
                *, 
                managed_identities = ..., 
                token_service_endpoint: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ManagedIdentityAzureBlobBackupStorageDescription(BackupStorageDescription):

        def __init__(
                self, 
                *, 
                blob_service_uri: str, 
                container_name: str, 
                friendly_name: str = ..., 
                managed_identity_type, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ManagedIdentityType(str, Enum):
        cluster = "Cluster"
        invalid = "Invalid"
        vmss = "VMSS"


    class azure.servicefabric.models.MetricLoadDescription(Model):

        def __init__(
                self, 
                *, 
                current_load: int = ..., 
                metric_name: str = ..., 
                predicted_load: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.MonitoringPolicyDescription(Model):

        def __init__(
                self, 
                *, 
                failure_action = ..., 
                health_check_retry_timeout_in_milliseconds: str = ..., 
                health_check_stable_duration_in_milliseconds: str = ..., 
                health_check_wait_duration_in_milliseconds: str = ..., 
                upgrade_domain_timeout_in_milliseconds: str = ..., 
                upgrade_timeout_in_milliseconds: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.MoveCost(str, Enum):
        high = "High"
        low = "Low"
        medium = "Medium"
        very_high = "VeryHigh"
        zero = "Zero"


    class azure.servicefabric.models.NameDescription(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NamedPartitionInformation(PartitionInformation):

        def __init__(
                self, 
                *, 
                id: str = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NamedPartitionSchemeDescription(PartitionSchemeDescription):

        def __init__(
                self, 
                *, 
                count: int, 
                names, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NetworkKind(str, Enum):
        local = "Local"


    class azure.servicefabric.models.NetworkRef(Model):

        def __init__(
                self, 
                *, 
                endpoint_refs = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NetworkResourceDescription(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                properties, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NetworkResourceProperties(NetworkResourcePropertiesBase):
        status: Union[str, ResourceStatus]
        status_details: str

        def __init__(
                self, 
                *, 
                description: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NetworkResourcePropertiesBase(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.NodeAbortedEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fault_domain: str, 
                has_correlated_events: bool = ..., 
                hostname: str, 
                ip_address_or_fqdn: str, 
                is_seed_node: bool, 
                node_id: str, 
                node_instance: int, 
                node_name: str, 
                node_version: str, 
                time_stamp, 
                upgrade_domain: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeAddedToClusterEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fabric_version: str, 
                has_correlated_events: bool = ..., 
                ip_address_or_fqdn: str, 
                node_capacities: str, 
                node_id: str, 
                node_instance: int, 
                node_name: str, 
                node_type: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeClosedEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                error: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                node_id: str, 
                node_instance: int, 
                node_name: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeDeactivateCompletedEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                batch_ids_with_deactivate_intent: str, 
                category: str = ..., 
                effective_deactivate_intent: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                node_instance: int, 
                node_name: str, 
                start_time, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeDeactivateStartedEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                batch_id: str, 
                category: str = ..., 
                deactivate_intent: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                node_instance: int, 
                node_name: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeDeactivationInfo(Model):

        def __init__(
                self, 
                *, 
                node_deactivation_intent = ..., 
                node_deactivation_status = ..., 
                node_deactivation_task = ..., 
                pending_safety_checks = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeDeactivationIntent(str, Enum):
        invalid = "Invalid"
        pause = "Pause"
        remove_data = "RemoveData"
        remove_node = "RemoveNode"
        restart = "Restart"


    class azure.servicefabric.models.NodeDeactivationStatus(str, Enum):
        completed = "Completed"
        none = "None"
        safety_check_complete = "SafetyCheckComplete"
        safety_check_in_progress = "SafetyCheckInProgress"


    class azure.servicefabric.models.NodeDeactivationTask(Model):

        def __init__(
                self, 
                *, 
                node_deactivation_intent = ..., 
                node_deactivation_task_id = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeDeactivationTaskId(Model):

        def __init__(
                self, 
                *, 
                id: str = ..., 
                node_deactivation_task_type = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeDeactivationTaskType(str, Enum):
        client = "Client"
        infrastructure = "Infrastructure"
        invalid = "Invalid"
        repair = "Repair"


    class azure.servicefabric.models.NodeDownEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                last_node_up_at, 
                node_instance: int, 
                node_name: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeEvent(FabricEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                node_name: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                health_events = ..., 
                health_statistics = ..., 
                name: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                node_name: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeHealthReportExpiredEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                node_instance_id: int, 
                node_name: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeHealthState(EntityHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                id = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeHealthStateChunk(EntityHealthStateChunk):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                node_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeHealthStateChunkList(EntityHealthStateChunkList):

        def __init__(
                self, 
                *, 
                items = ..., 
                total_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeHealthStateFilter(Model):

        def __init__(
                self, 
                *, 
                health_state_filter: int = 0, 
                node_name_filter: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeId(Model):

        def __init__(
                self, 
                *, 
                id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeImpact(Model):

        def __init__(
                self, 
                *, 
                impact_level = ..., 
                node_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeInfo(Model):

        def __init__(
                self, 
                *, 
                code_version: str = ..., 
                config_version: str = ..., 
                fault_domain: str = ..., 
                health_state = ..., 
                id = ..., 
                infrastructure_placement_id: str = ..., 
                instance_id: str = ..., 
                ip_address_or_fqdn: str = ..., 
                is_node_by_node_upgrade_in_progress: bool = ..., 
                is_seed_node: bool = ..., 
                is_stopped: bool = ..., 
                name: str = ..., 
                node_deactivation_info = ..., 
                node_down_at = ..., 
                node_down_time_in_seconds: str = ..., 
                node_status = ..., 
                node_tags = ..., 
                node_up_at = ..., 
                node_up_time_in_seconds: str = ..., 
                type: str = ..., 
                upgrade_domain: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeLoadInfo(Model):

        def __init__(
                self, 
                *, 
                node_load_metric_information = ..., 
                node_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeLoadMetricInformation(Model):

        def __init__(
                self, 
                *, 
                buffered_node_capacity_remaining: str = ..., 
                current_node_load: str = ..., 
                is_capacity_violation: bool = ..., 
                name: str = ..., 
                node_buffered_capacity: str = ..., 
                node_capacity: str = ..., 
                node_capacity_remaining: str = ..., 
                node_load: str = ..., 
                node_remaining_buffered_capacity: str = ..., 
                node_remaining_capacity: str = ..., 
                planned_node_load_removal: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeNewHealthReportEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                node_instance_id: int, 
                node_name: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeOpenFailedEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                error: str, 
                event_instance_id: str, 
                fault_domain: str, 
                has_correlated_events: bool = ..., 
                hostname: str, 
                ip_address_or_fqdn: str, 
                is_seed_node: bool, 
                node_id: str, 
                node_instance: int, 
                node_name: str, 
                node_version: str, 
                time_stamp, 
                upgrade_domain: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeOpenSucceededEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fault_domain: str, 
                has_correlated_events: bool = ..., 
                hostname: str, 
                ip_address_or_fqdn: str, 
                is_seed_node: bool, 
                node_id: str, 
                node_instance: int, 
                node_name: str, 
                node_version: str, 
                time_stamp, 
                upgrade_domain: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeRemovedFromClusterEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                fabric_version: str, 
                has_correlated_events: bool = ..., 
                ip_address_or_fqdn: str, 
                node_capacities: str, 
                node_id: str, 
                node_instance: int, 
                node_name: str, 
                node_type: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeRepairImpactDescription(RepairImpactDescriptionBase):

        def __init__(
                self, 
                *, 
                node_impact_list = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeRepairTargetDescription(RepairTargetDescriptionBase):

        def __init__(
                self, 
                *, 
                node_names = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeResult(Model):

        def __init__(
                self, 
                *, 
                node_instance_id: str = ..., 
                node_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeStatus(str, Enum):
        disabled = "Disabled"
        disabling = "Disabling"
        down = "Down"
        enabling = "Enabling"
        invalid = "Invalid"
        removed = "Removed"
        unknown = "Unknown"
        up = "Up"


    class azure.servicefabric.models.NodeStatusFilter(str, Enum):
        all = "all"
        default = "default"
        disabled = "disabled"
        disabling = "disabling"
        down = "down"
        enabling = "enabling"
        removed = "removed"
        unknown = "unknown"
        up = "up"


    class azure.servicefabric.models.NodeTagsDescription(Model):

        def __init__(
                self, 
                *, 
                count: int, 
                tags, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeTransitionProgress(Model):

        def __init__(
                self, 
                *, 
                node_transition_result = ..., 
                state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeTransitionResult(Model):

        def __init__(
                self, 
                *, 
                error_code: int = ..., 
                node_result = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeTransitionType(str, Enum):
        invalid = "Invalid"
        start = "Start"
        stop = "Stop"


    class azure.servicefabric.models.NodeTypeHealthPolicyMapItem(Model):

        def __init__(
                self, 
                *, 
                key: str, 
                value: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeTypeNodesHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_nodes: int = ..., 
                node_type_name: str = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeUpEvent(NodeEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                last_node_down_at, 
                node_instance: int, 
                node_name: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodeUpgradePhase(str, Enum):
        invalid = "Invalid"
        post_upgrade_safety_check = "PostUpgradeSafetyCheck"
        pre_upgrade_safety_check = "PreUpgradeSafetyCheck"
        upgrading = "Upgrading"


    class azure.servicefabric.models.NodeUpgradeProgressInfo(Model):

        def __init__(
                self, 
                *, 
                node_name: str = ..., 
                pending_safety_checks = ..., 
                upgrade_duration: str = ..., 
                upgrade_phase = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.NodesHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_nodes: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.OperatingSystemType(str, Enum):
        linux = "Linux"
        windows = "Windows"


    class azure.servicefabric.models.OperationState(str, Enum):
        cancelled = "Cancelled"
        completed = "Completed"
        faulted = "Faulted"
        force_cancelled = "ForceCancelled"
        invalid = "Invalid"
        rolling_back = "RollingBack"
        running = "Running"


    class azure.servicefabric.models.OperationStatus(Model):

        def __init__(
                self, 
                *, 
                operation_id: str = ..., 
                state = ..., 
                type = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.OperationType(str, Enum):
        invalid = "Invalid"
        node_transition = "NodeTransition"
        partition_data_loss = "PartitionDataLoss"
        partition_quorum_loss = "PartitionQuorumLoss"
        partition_restart = "PartitionRestart"


    class azure.servicefabric.models.Ordering(str, Enum):
        asc = "Asc"
        desc = "Desc"


    class azure.servicefabric.models.PackageSharingPolicyInfo(Model):

        def __init__(
                self, 
                *, 
                package_sharing_scope = ..., 
                shared_package_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PackageSharingPolicyScope(str, Enum):
        all = "All"
        code = "Code"
        config = "Config"
        data = "Data"
        none = "None"


    class azure.servicefabric.models.PagedApplicationInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedApplicationResourceDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedApplicationTypeInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedBackupConfigurationInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedBackupEntityList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedBackupInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedBackupPolicyDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedComposeDeploymentStatusInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedDeployedApplicationInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedGatewayResourceDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedNetworkResourceDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedNodeInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedPropertyInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                is_consistent: bool = ..., 
                properties = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedReplicaInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedSecretResourceDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedSecretValueResourceDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedServiceInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedServicePartitionInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedServiceReplicaDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedServiceResourceDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedSubNameInfoList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                is_consistent: bool = ..., 
                sub_names = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedUpdatePartitionLoadResultList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PagedVolumeResourceDescriptionList(Model):

        def __init__(
                self, 
                *, 
                continuation_token: str = ..., 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionAccessStatus(str, Enum):
        granted = "Granted"
        invalid = "Invalid"
        no_write_quorum = "NoWriteQuorum"
        not_primary = "NotPrimary"
        reconfiguration_pending = "ReconfigurationPending"


    class azure.servicefabric.models.PartitionAnalysisEvent(PartitionEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                metadata, 
                partition_id: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionBackupConfigurationInfo(BackupConfigurationInfo):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                policy_inherited_from = ..., 
                policy_name: str = ..., 
                service_name: str = ..., 
                suspension_info = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionBackupEntity(BackupEntity):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionDataLossProgress(Model):

        def __init__(
                self, 
                *, 
                invoke_data_loss_result = ..., 
                state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionEvent(FabricEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                partition_id: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                health_events = ..., 
                health_statistics = ..., 
                partition_id: str = ..., 
                replica_health_states = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                partition_id: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionHealthReportExpiredEvent(PartitionEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                partition_id: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionHealthState(EntityHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionHealthStateChunk(EntityHealthStateChunk):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                partition_id: str = ..., 
                replica_health_state_chunks = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionHealthStateChunkList(Model):

        def __init__(
                self, 
                *, 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionHealthStateFilter(Model):

        def __init__(
                self, 
                *, 
                health_state_filter: int = 0, 
                partition_id_filter: str = ..., 
                replica_filters = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionInformation(Model):

        def __init__(
                self, 
                *, 
                id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionInstanceCountScaleMechanism(ScalingMechanismDescription):

        def __init__(
                self, 
                *, 
                max_instance_count: int, 
                min_instance_count: int, 
                scale_increment: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionLoadInformation(Model):

        def __init__(
                self, 
                *, 
                auxiliary_load_metric_reports = ..., 
                partition_id: str = ..., 
                primary_load_metric_reports = ..., 
                secondary_load_metric_reports = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionMetricLoadDescription(Model):

        def __init__(
                self, 
                *, 
                auxiliary_replica_load_entries_per_node = ..., 
                auxiliary_replicas_load_entries = ..., 
                partition_id: str = ..., 
                primary_replica_load_entries = ..., 
                secondary_replica_or_instance_load_entries_per_node = ..., 
                secondary_replicas_or_instances_load_entries = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionNewHealthReportEvent(PartitionEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                partition_id: str, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionPrimaryMoveAnalysisEvent(PartitionAnalysisEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                current_node: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                metadata, 
                move_reason: str, 
                partition_id: str, 
                previous_node: str, 
                relevant_traces: str, 
                time_stamp, 
                when_move_completed, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionQuorumLossProgress(Model):

        def __init__(
                self, 
                *, 
                invoke_quorum_loss_result = ..., 
                state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionReconfiguredEvent(PartitionEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                cc_epoch_config_version: int, 
                cc_epoch_data_loss_version: int, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                node_instance_id: str, 
                node_name: str, 
                partition_id: str, 
                phase0_duration_ms: float, 
                phase1_duration_ms: float, 
                phase2_duration_ms: float, 
                phase3_duration_ms: float, 
                phase4_duration_ms: float, 
                reconfig_type: str, 
                result: str, 
                service_type: str, 
                time_stamp, 
                total_duration_ms: float, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionRestartProgress(Model):

        def __init__(
                self, 
                *, 
                restart_partition_result = ..., 
                state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionSafetyCheck(SafetyCheck):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PartitionScheme(str, Enum):
        invalid = "Invalid"
        named = "Named"
        singleton = "Singleton"
        uniform_int64_range = "UniformInt64Range"


    class azure.servicefabric.models.PartitionSchemeDescription(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.PartitionsHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_partitions_per_service: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PrimaryReplicatorStatus(ReplicatorStatus):

        def __init__(
                self, 
                *, 
                remote_replicators = ..., 
                replication_queue_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.Probe(Model):

        def __init__(
                self, 
                *, 
                exec_property = ..., 
                failure_threshold: int = 3, 
                http_get = ..., 
                initial_delay_seconds: int = 0, 
                period_seconds: int = 10, 
                success_threshold: int = 1, 
                tcp_socket = ..., 
                timeout_seconds: int = 1, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ProbeExec(Model):

        def __init__(
                self, 
                *, 
                command: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ProbeHttpGet(Model):

        def __init__(
                self, 
                *, 
                host: str = ..., 
                http_headers = ..., 
                path: str = ..., 
                port: int, 
                scheme = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ProbeHttpGetHeaders(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                value: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ProbeTcpSocket(Model):

        def __init__(
                self, 
                *, 
                port: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PropertyBatchDescriptionList(Model):

        def __init__(
                self, 
                *, 
                operations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PropertyBatchInfo(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.PropertyBatchInfoKind(str, Enum):
        failed = "Failed"
        invalid = "Invalid"
        successful = "Successful"


    class azure.servicefabric.models.PropertyBatchOperation(Model):

        def __init__(
                self, 
                *, 
                property_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PropertyBatchOperationKind(str, Enum):
        check_exists = "CheckExists"
        check_sequence = "CheckSequence"
        check_value = "CheckValue"
        delete = "Delete"
        get = "Get"
        invalid = "Invalid"
        put = "Put"


    class azure.servicefabric.models.PropertyDescription(Model):

        def __init__(
                self, 
                *, 
                custom_type_id: str = ..., 
                property_name: str, 
                value, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PropertyInfo(Model):

        def __init__(
                self, 
                *, 
                metadata, 
                name: str, 
                value = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PropertyMetadata(Model):

        def __init__(
                self, 
                *, 
                custom_type_id: str = ..., 
                last_modified_utc_timestamp = ..., 
                parent: str = ..., 
                sequence_number: str = ..., 
                size_in_bytes: int = ..., 
                type_id = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PropertyValue(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.PropertyValueKind(str, Enum):
        binary = "Binary"
        double = "Double"
        guid = "Guid"
        int64 = "Int64"
        invalid = "Invalid"
        string = "String"


    class azure.servicefabric.models.ProvisionApplicationTypeDescription(ProvisionApplicationTypeDescriptionBase):

        def __init__(
                self, 
                *, 
                application_package_cleanup_policy = ..., 
                application_type_build_path: str, 
                async_property: bool, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ProvisionApplicationTypeDescriptionBase(Model):

        def __init__(
                self, 
                *, 
                async_property: bool, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ProvisionApplicationTypeKind(str, Enum):
        external_store = "ExternalStore"
        image_store_path = "ImageStorePath"
        invalid = "Invalid"


    class azure.servicefabric.models.ProvisionFabricDescription(Model):

        def __init__(
                self, 
                *, 
                cluster_manifest_file_path: str = ..., 
                code_file_path: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.PutPropertyBatchOperation(PropertyBatchOperation):

        def __init__(
                self, 
                *, 
                custom_type_id: str = ..., 
                property_name: str, 
                value, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.QuorumLossMode(str, Enum):
        all_replicas = "AllReplicas"
        invalid = "Invalid"
        quorum_replicas = "QuorumReplicas"


    class azure.servicefabric.models.ReconfigurationInformation(Model):

        def __init__(
                self, 
                *, 
                previous_configuration_role = ..., 
                reconfiguration_phase = ..., 
                reconfiguration_start_time_utc = ..., 
                reconfiguration_type = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReconfigurationPhase(str, Enum):
        abort_phase_zero = "AbortPhaseZero"
        none = "None"
        phase0 = "Phase0"
        phase1 = "Phase1"
        phase2 = "Phase2"
        phase3 = "Phase3"
        phase4 = "Phase4"
        unknown = "Unknown"


    class azure.servicefabric.models.ReconfigurationType(str, Enum):
        failover = "Failover"
        other = "Other"
        swap_primary = "SwapPrimary"
        unknown = "Unknown"


    class azure.servicefabric.models.RegistryCredential(Model):

        def __init__(
                self, 
                *, 
                password_encrypted: bool = ..., 
                registry_password: str = ..., 
                registry_user_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReliableCollectionsRef(Model):

        def __init__(
                self, 
                *, 
                do_not_persist_state: bool = ..., 
                name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RemoteReplicatorAcknowledgementDetail(Model):

        def __init__(
                self, 
                *, 
                average_apply_duration: str = ..., 
                average_receive_duration: str = ..., 
                not_received_count: str = ..., 
                received_and_not_applied_count: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RemoteReplicatorAcknowledgementStatus(Model):

        def __init__(
                self, 
                *, 
                copy_stream_acknowledgement_detail = ..., 
                replication_stream_acknowledgement_detail = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RemoteReplicatorStatus(Model):

        def __init__(
                self, 
                *, 
                is_in_build: bool = ..., 
                last_acknowledgement_processed_time_utc = ..., 
                last_applied_copy_sequence_number: str = ..., 
                last_applied_replication_sequence_number: str = ..., 
                last_received_copy_sequence_number: str = ..., 
                last_received_replication_sequence_number: str = ..., 
                remote_replicator_acknowledgement_status = ..., 
                replica_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RepairImpactDescriptionBase(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.RepairImpactKind(str, Enum):
        invalid = "Invalid"
        node = "Node"


    class azure.servicefabric.models.RepairTargetDescriptionBase(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.RepairTargetKind(str, Enum):
        invalid = "Invalid"
        node = "Node"


    class azure.servicefabric.models.RepairTask(Model):

        def __init__(
                self, 
                *, 
                action: str, 
                description: str = ..., 
                executor: str = ..., 
                executor_data: str = ..., 
                flags: int = ..., 
                history = ..., 
                impact = ..., 
                perform_preparing_health_check: bool = ..., 
                perform_restoring_health_check: bool = ..., 
                preparing_health_check_state = ..., 
                restoring_health_check_state = ..., 
                result_code: int = ..., 
                result_details: str = ..., 
                result_status = ..., 
                state, 
                target = ..., 
                task_id: str, 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RepairTaskApproveDescription(Model):

        def __init__(
                self, 
                *, 
                task_id: str, 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RepairTaskCancelDescription(Model):

        def __init__(
                self, 
                *, 
                request_abort: bool = ..., 
                task_id: str, 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RepairTaskDeleteDescription(Model):

        def __init__(
                self, 
                *, 
                task_id: str, 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RepairTaskHealthCheckState(str, Enum):
        in_progress = "InProgress"
        not_started = "NotStarted"
        skipped = "Skipped"
        succeeded = "Succeeded"
        timed_out = "TimedOut"


    class azure.servicefabric.models.RepairTaskHistory(Model):

        def __init__(
                self, 
                *, 
                approved_utc_timestamp = ..., 
                claimed_utc_timestamp = ..., 
                completed_utc_timestamp = ..., 
                created_utc_timestamp = ..., 
                executing_utc_timestamp = ..., 
                preparing_health_check_end_utc_timestamp = ..., 
                preparing_health_check_start_utc_timestamp = ..., 
                preparing_utc_timestamp = ..., 
                restoring_health_check_end_utc_timestamp = ..., 
                restoring_health_check_start_utc_timestamp = ..., 
                restoring_utc_timestamp = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RepairTaskUpdateHealthPolicyDescription(Model):

        def __init__(
                self, 
                *, 
                perform_preparing_health_check: bool = ..., 
                perform_restoring_health_check: bool = ..., 
                task_id: str, 
                version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RepairTaskUpdateInfo(Model):

        def __init__(
                self, 
                *, 
                version: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaEvent(FabricEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                partition_id: str, 
                replica_id: int, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                health_events = ..., 
                health_statistics = ..., 
                partition_id: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                partition_id: str = ..., 
                replica_or_instance_id: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaHealthReportServiceKind(str, Enum):
        stateful = "Stateful"
        stateless = "Stateless"


    class azure.servicefabric.models.ReplicaHealthState(EntityHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaHealthStateChunk(EntityHealthStateChunk):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                replica_or_instance_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaHealthStateChunkList(Model):

        def __init__(
                self, 
                *, 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaHealthStateFilter(Model):

        def __init__(
                self, 
                *, 
                health_state_filter: int = 0, 
                replica_or_instance_id_filter: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaInfo(Model):

        def __init__(
                self, 
                *, 
                address: str = ..., 
                health_state = ..., 
                last_in_build_duration_in_seconds: str = ..., 
                node_name: str = ..., 
                replica_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaKind(str, Enum):
        invalid = "Invalid"
        key_value_store = "KeyValueStore"


    class azure.servicefabric.models.ReplicaLifecycleDescription(Model):

        def __init__(
                self, 
                *, 
                is_singleton_replica_move_allowed_during_upgrade: bool = ..., 
                restore_replica_location_after_upgrade: bool = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaMetricLoadDescription(Model):

        def __init__(
                self, 
                *, 
                node_name: str = ..., 
                replica_or_instance_load_entries = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicaRole(str, Enum):
        active_auxiliary = "ActiveAuxiliary"
        active_secondary = "ActiveSecondary"
        idle_auxiliary = "IdleAuxiliary"
        idle_secondary = "IdleSecondary"
        none = "None"
        primary = "Primary"
        primary_auxiliary = "PrimaryAuxiliary"
        unknown = "Unknown"


    class azure.servicefabric.models.ReplicaStatus(str, Enum):
        down = "Down"
        dropped = "Dropped"
        in_build = "InBuild"
        invalid = "Invalid"
        ready = "Ready"
        standby = "Standby"


    class azure.servicefabric.models.ReplicaStatusBase(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.ReplicasHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_replicas_per_partition: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicatorOperationName(str, Enum):
        abort = "Abort"
        build = "Build"
        change_role = "ChangeRole"
        close = "Close"
        invalid = "Invalid"
        none = "None"
        on_data_loss = "OnDataLoss"
        open = "Open"
        update_epoch = "UpdateEpoch"
        wait_for_catchup = "WaitForCatchup"


    class azure.servicefabric.models.ReplicatorQueueStatus(Model):

        def __init__(
                self, 
                *, 
                committed_sequence_number: str = ..., 
                completed_sequence_number: str = ..., 
                first_sequence_number: str = ..., 
                last_sequence_number: str = ..., 
                queue_memory_size: str = ..., 
                queue_utilization_percentage: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ReplicatorStatus(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.ResolvedServiceEndpoint(Model):

        def __init__(
                self, 
                *, 
                address: str = ..., 
                kind = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ResolvedServicePartition(Model):

        def __init__(
                self, 
                *, 
                endpoints, 
                name: str, 
                partition_information, 
                version: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ResourceLimits(Model):

        def __init__(
                self, 
                *, 
                cpu: float = ..., 
                memory_in_gb: float = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ResourceRequests(Model):

        def __init__(
                self, 
                *, 
                cpu: float, 
                memory_in_gb: float, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ResourceRequirements(Model):

        def __init__(
                self, 
                *, 
                limits = ..., 
                requests, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ResourceStatus(str, Enum):
        creating = "Creating"
        deleting = "Deleting"
        failed = "Failed"
        ready = "Ready"
        unknown = "Unknown"
        upgrading = "Upgrading"


    class azure.servicefabric.models.RestartDeployedCodePackageDescription(Model):

        def __init__(
                self, 
                *, 
                code_package_instance_id: str, 
                code_package_name: str, 
                service_manifest_name: str, 
                service_package_activation_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RestartNodeDescription(Model):

        def __init__(
                self, 
                *, 
                create_fabric_dump = "False", 
                node_instance_id: str = "0", 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RestartPartitionMode(str, Enum):
        all_replicas_or_instances = "AllReplicasOrInstances"
        invalid = "Invalid"
        only_active_secondaries = "OnlyActiveSecondaries"


    class azure.servicefabric.models.RestartPartitionResult(Model):

        def __init__(
                self, 
                *, 
                error_code: int = ..., 
                selected_partition = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RestartPolicy(str, Enum):
        never = "Never"
        on_failure = "OnFailure"


    class azure.servicefabric.models.RestorePartitionDescription(Model):

        def __init__(
                self, 
                *, 
                backup_id: str, 
                backup_location: str, 
                backup_storage = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RestoreProgressInfo(Model):

        def __init__(
                self, 
                *, 
                failure_error = ..., 
                restore_state = ..., 
                restored_epoch = ..., 
                restored_lsn: str = ..., 
                time_stamp_utc = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RestoreState(str, Enum):
        accepted = "Accepted"
        failure = "Failure"
        invalid = "Invalid"
        restore_in_progress = "RestoreInProgress"
        success = "Success"
        timeout = "Timeout"


    class azure.servicefabric.models.ResultStatus(str, Enum):
        cancelled = "Cancelled"
        failed = "Failed"
        interrupted = "Interrupted"
        invalid = "Invalid"
        pending = "Pending"
        succeeded = "Succeeded"


    class azure.servicefabric.models.ResumeApplicationUpgradeDescription(Model):

        def __init__(
                self, 
                *, 
                upgrade_domain_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ResumeClusterUpgradeDescription(Model):

        def __init__(
                self, 
                *, 
                upgrade_domain: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RetentionPolicyDescription(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.RetentionPolicyType(str, Enum):
        basic = "Basic"
        invalid = "Invalid"


    class azure.servicefabric.models.RollingUpgradeMode(str, Enum):
        invalid = "Invalid"
        monitored = "Monitored"
        unmonitored_auto = "UnmonitoredAuto"
        unmonitored_manual = "UnmonitoredManual"


    class azure.servicefabric.models.RollingUpgradeUpdateDescription(Model):

        def __init__(
                self, 
                *, 
                failure_action = ..., 
                force_restart: bool = ..., 
                health_check_retry_timeout_in_milliseconds: str = ..., 
                health_check_stable_duration_in_milliseconds: str = ..., 
                health_check_wait_duration_in_milliseconds: str = ..., 
                instance_close_delay_duration_in_seconds: int = ..., 
                replica_set_check_timeout_in_milliseconds: int = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                upgrade_domain_timeout_in_milliseconds: str = ..., 
                upgrade_timeout_in_milliseconds: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.RunToCompletionExecutionPolicy(ExecutionPolicy):

        def __init__(
                self, 
                *, 
                restart, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SafetyCheck(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.SafetyCheckKind(str, Enum):
        ensure_availability = "EnsureAvailability"
        ensure_partition_quorum = "EnsurePartitionQuorum"
        ensure_seed_node_quorum = "EnsureSeedNodeQuorum"
        invalid = "Invalid"
        wait_for_inbuild_replica = "WaitForInbuildReplica"
        wait_for_primary_placement = "WaitForPrimaryPlacement"
        wait_for_primary_swap = "WaitForPrimarySwap"
        wait_for_reconfiguration = "WaitForReconfiguration"


    class azure.servicefabric.models.SafetyCheckWrapper(Model):

        def __init__(
                self, 
                *, 
                safety_check = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ScalingMechanismDescription(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.ScalingMechanismKind(str, Enum):
        add_remove_incremental_named_partition = "AddRemoveIncrementalNamedPartition"
        invalid = "Invalid"
        partition_instance_count = "PartitionInstanceCount"


    class azure.servicefabric.models.ScalingPolicyDescription(Model):

        def __init__(
                self, 
                *, 
                scaling_mechanism, 
                scaling_trigger, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ScalingTriggerDescription(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.ScalingTriggerKind(str, Enum):
        average_partition_load = "AveragePartitionLoad"
        average_service_load = "AverageServiceLoad"
        invalid = "Invalid"


    class azure.servicefabric.models.Scheme(str, Enum):
        http = "http"
        https = "https"


    class azure.servicefabric.models.SecondaryActiveReplicatorStatus(SecondaryReplicatorStatus):

        def __init__(
                self, 
                *, 
                copy_queue_status = ..., 
                is_in_build: bool = ..., 
                last_acknowledgement_sent_time_utc = ..., 
                last_copy_operation_received_time_utc = ..., 
                last_replication_operation_received_time_utc = ..., 
                replication_queue_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SecondaryIdleReplicatorStatus(SecondaryReplicatorStatus):

        def __init__(
                self, 
                *, 
                copy_queue_status = ..., 
                is_in_build: bool = ..., 
                last_acknowledgement_sent_time_utc = ..., 
                last_copy_operation_received_time_utc = ..., 
                last_replication_operation_received_time_utc = ..., 
                replication_queue_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SecondaryReplicatorStatus(ReplicatorStatus):

        def __init__(
                self, 
                *, 
                copy_queue_status = ..., 
                is_in_build: bool = ..., 
                last_acknowledgement_sent_time_utc = ..., 
                last_copy_operation_received_time_utc = ..., 
                last_replication_operation_received_time_utc = ..., 
                replication_queue_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SecretKind(str, Enum):
        inlined_value = "inlinedValue"
        key_vault_versioned_reference = "keyVaultVersionedReference"


    class azure.servicefabric.models.SecretResourceDescription(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                properties, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SecretResourceProperties(SecretResourcePropertiesBase):
        status: Union[str, ResourceStatus]
        status_details: str

        def __init__(
                self, 
                *, 
                content_type: str = ..., 
                description: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SecretResourcePropertiesBase(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.SecretValue(Model):

        def __init__(
                self, 
                *, 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SecretValueProperties(Model):

        def __init__(
                self, 
                *, 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SecretValueResourceDescription(Model):

        def __init__(
                self, 
                *, 
                name: str, 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SeedNodeSafetyCheck(SafetyCheck):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.SelectedPartition(Model):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceBackupConfigurationInfo(BackupConfigurationInfo):

        def __init__(
                self, 
                *, 
                policy_inherited_from = ..., 
                policy_name: str = ..., 
                service_name: str = ..., 
                suspension_info = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceBackupEntity(BackupEntity):

        def __init__(
                self, 
                *, 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceCorrelationDescription(Model):

        def __init__(
                self, 
                *, 
                scheme, 
                service_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceCorrelationScheme(str, Enum):
        affinity = "Affinity"
        aligned_affinity = "AlignedAffinity"
        invalid = "Invalid"
        non_aligned_affinity = "NonAlignedAffinity"


    class azure.servicefabric.models.ServiceCreatedEvent(ServiceEvent):

        def __init__(
                self, 
                *, 
                application_name: str, 
                application_type_name: str, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                is_stateful: bool, 
                min_replica_set_size: int, 
                partition_count: int, 
                partition_id: str, 
                service_id: str, 
                service_instance: int, 
                service_package_version: str, 
                service_type_name: str, 
                target_replica_set_size: int, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceDeletedEvent(ServiceEvent):

        def __init__(
                self, 
                *, 
                application_name: str, 
                application_type_name: str, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                is_stateful: bool, 
                min_replica_set_size: int, 
                partition_count: int, 
                service_id: str, 
                service_instance: int, 
                service_package_version: str, 
                service_type_name: str, 
                target_replica_set_size: int, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceDescription(Model):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                correlation_scheme = ..., 
                default_move_cost = ..., 
                initialization_data = ..., 
                is_default_move_cost_specified: bool = ..., 
                partition_description, 
                placement_constraints: str = ..., 
                scaling_policies = ..., 
                service_dns_name: str = ..., 
                service_load_metrics = ..., 
                service_name: str, 
                service_package_activation_mode = ..., 
                service_placement_policies = ..., 
                service_type_name: str, 
                tags_required_to_place = ..., 
                tags_required_to_run = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceEndpointRole(str, Enum):
        invalid = "Invalid"
        stateful_primary = "StatefulPrimary"
        stateful_secondary = "StatefulSecondary"
        stateless = "Stateless"


    class azure.servicefabric.models.ServiceEvent(FabricEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                service_id: str, 
                time_stamp, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceFromTemplateDescription(Model):

        def __init__(
                self, 
                *, 
                application_name: str, 
                initialization_data = ..., 
                service_dns_name: str = ..., 
                service_name: str, 
                service_package_activation_mode = ..., 
                service_type_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHealth(EntityHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                health_events = ..., 
                health_statistics = ..., 
                name: str = ..., 
                partition_health_states = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                service_name: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHealthReportExpiredEvent(ServiceEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                instance_id: int, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                service_id: str, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHealthState(EntityHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHealthStateChunk(EntityHealthStateChunk):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                partition_health_state_chunks = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHealthStateChunkList(Model):

        def __init__(
                self, 
                *, 
                items = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHealthStateFilter(Model):

        def __init__(
                self, 
                *, 
                health_state_filter: int = 0, 
                partition_filters = ..., 
                service_name_filter: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceHostUpgradeImpact(str, Enum):
        invalid = "Invalid"
        none = "None"
        service_host_restart = "ServiceHostRestart"
        unexpected_service_host_restart = "UnexpectedServiceHostRestart"


    class azure.servicefabric.models.ServiceIdentity(Model):

        def __init__(
                self, 
                *, 
                identity_ref: str = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceInfo(Model):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                id: str = ..., 
                is_service_group: bool = ..., 
                manifest_version: str = ..., 
                name: str = ..., 
                service_status = ..., 
                type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceKind(str, Enum):
        invalid = "Invalid"
        stateful = "Stateful"
        stateless = "Stateless"


    class azure.servicefabric.models.ServiceLoadMetricDescription(Model):

        def __init__(
                self, 
                *, 
                auxiliary_default_load: int = ..., 
                default_load: int = ..., 
                name: str, 
                primary_default_load: int = ..., 
                secondary_default_load: int = ..., 
                weight = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceLoadMetricWeight(str, Enum):
        high = "High"
        low = "Low"
        medium = "Medium"
        zero = "Zero"


    class azure.servicefabric.models.ServiceNameInfo(Model):

        def __init__(
                self, 
                *, 
                id: str = ..., 
                name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceNewHealthReportEvent(ServiceEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                instance_id: int, 
                property: str, 
                remove_when_expired: bool, 
                sequence_number: int, 
                service_id: str, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceOperationName(str, Enum):
        abort = "Abort"
        change_role = "ChangeRole"
        close = "Close"
        none = "None"
        open = "Open"
        unknown = "Unknown"


    class azure.servicefabric.models.ServicePackageActivationMode(str, Enum):
        exclusive_process = "ExclusiveProcess"
        shared_process = "SharedProcess"


    class azure.servicefabric.models.ServicePartitionInfo(Model):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                partition_information = ..., 
                partition_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServicePartitionKind(str, Enum):
        int64_range = "Int64Range"
        invalid = "Invalid"
        named = "Named"
        singleton = "Singleton"


    class azure.servicefabric.models.ServicePartitionStatus(str, Enum):
        deleting = "Deleting"
        in_quorum_loss = "InQuorumLoss"
        invalid = "Invalid"
        not_ready = "NotReady"
        ready = "Ready"
        reconfiguring = "Reconfiguring"


    class azure.servicefabric.models.ServicePlacementAllowMultipleStatelessInstancesOnNodePolicyDescription(ServicePlacementPolicyDescription):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServicePlacementInvalidDomainPolicyDescription(ServicePlacementPolicyDescription):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServicePlacementNonPartiallyPlaceServicePolicyDescription(ServicePlacementPolicyDescription):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.ServicePlacementPolicyDescription(Model):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.ServicePlacementPolicyType(str, Enum):
        allow_multiple_stateless_instances_on_node = "AllowMultipleStatelessInstancesOnNode"
        invalid = "Invalid"
        invalid_domain = "InvalidDomain"
        non_partially_place_service = "NonPartiallyPlaceService"
        prefer_primary_domain = "PreferPrimaryDomain"
        require_domain = "RequireDomain"
        require_domain_distribution = "RequireDomainDistribution"


    class azure.servicefabric.models.ServicePlacementPreferPrimaryDomainPolicyDescription(ServicePlacementPolicyDescription):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServicePlacementRequireDomainDistributionPolicyDescription(ServicePlacementPolicyDescription):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServicePlacementRequiredDomainPolicyDescription(ServicePlacementPolicyDescription):

        def __init__(
                self, 
                *, 
                domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceProperties(Model):
        health_state: Union[str, HealthState]
        status: Union[str, ResourceStatus]
        status_details: str
        unhealthy_evaluation: str

        def __init__(
                self, 
                *, 
                auto_scaling_policies = ..., 
                description: str = ..., 
                dns_name: str = ..., 
                execution_policy = ..., 
                identity_refs = ..., 
                replica_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceReplicaDescription(ServiceReplicaProperties):

        def __init__(
                self, 
                *, 
                code_packages, 
                diagnostics = ..., 
                network_refs = ..., 
                os_type, 
                replica_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceReplicaProperties(Model):

        def __init__(
                self, 
                *, 
                code_packages, 
                diagnostics = ..., 
                network_refs = ..., 
                os_type, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceResourceDescription(Model):
        health_state: Union[str, HealthState]
        status: Union[str, ResourceStatus]
        status_details: str
        unhealthy_evaluation: str

        def __init__(
                self, 
                *, 
                auto_scaling_policies = ..., 
                code_packages, 
                description: str = ..., 
                diagnostics = ..., 
                dns_name: str = ..., 
                execution_policy = ..., 
                identity_refs = ..., 
                name: str, 
                network_refs = ..., 
                os_type, 
                replica_count: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceStatus(str, Enum):
        active = "Active"
        creating = "Creating"
        deleting = "Deleting"
        failed = "Failed"
        unknown = "Unknown"
        upgrading = "Upgrading"


    class azure.servicefabric.models.ServiceTypeDescription(Model):

        def __init__(
                self, 
                *, 
                extensions = ..., 
                is_stateful: bool = ..., 
                load_metrics = ..., 
                placement_constraints: str = ..., 
                service_placement_policies = ..., 
                service_type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceTypeExtensionDescription(Model):

        def __init__(
                self, 
                *, 
                key: str = ..., 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceTypeHealthPolicy(Model):

        def __init__(
                self, 
                *, 
                max_percent_unhealthy_partitions_per_service: int = 0, 
                max_percent_unhealthy_replicas_per_partition: int = 0, 
                max_percent_unhealthy_services: int = 0, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceTypeHealthPolicyMapItem(Model):

        def __init__(
                self, 
                *, 
                key: str, 
                value, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceTypeInfo(Model):

        def __init__(
                self, 
                *, 
                is_service_group: bool = ..., 
                service_manifest_name: str = ..., 
                service_manifest_version: str = ..., 
                service_type_description = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceTypeManifest(Model):

        def __init__(
                self, 
                *, 
                manifest: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceTypeRegistrationStatus(str, Enum):
        disabled = "Disabled"
        enabled = "Enabled"
        invalid = "Invalid"
        registered = "Registered"


    class azure.servicefabric.models.ServiceUpdateDescription(Model):

        def __init__(
                self, 
                *, 
                correlation_scheme = ..., 
                default_move_cost = ..., 
                flags: str = ..., 
                load_metrics = ..., 
                placement_constraints: str = ..., 
                scaling_policies = ..., 
                service_dns_name: str = ..., 
                service_placement_policies = ..., 
                tags_for_placement = ..., 
                tags_for_running = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServiceUpgradeProgress(Model):

        def __init__(
                self, 
                *, 
                completed_replica_count: str = ..., 
                pending_replica_count: str = ..., 
                service_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ServicesHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_services: int = ..., 
                service_type_name: str = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.Setting(Model):

        def __init__(
                self, 
                *, 
                name: str = ..., 
                type = "ClearText", 
                value: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SettingType(str, Enum):
        clear_text = "ClearText"
        key_vault_reference = "KeyVaultReference"
        secret_value_reference = "SecretValueReference"


    class azure.servicefabric.models.SingletonPartitionInformation(PartitionInformation):

        def __init__(
                self, 
                *, 
                id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SingletonPartitionSchemeDescription(PartitionSchemeDescription):

        def __init__(self, **kwargs) -> None: ...


    class azure.servicefabric.models.SizeTypes(str, Enum):
        large = "Large"
        medium = "Medium"
        small = "Small"


    class azure.servicefabric.models.StartClusterUpgradeDescription(Model):

        def __init__(
                self, 
                *, 
                application_health_policy_map = ..., 
                cluster_health_policy = ..., 
                cluster_upgrade_health_policy = ..., 
                code_version: str = ..., 
                config_version: str = ..., 
                enable_delta_health_evaluation: bool = ..., 
                force_restart: bool = ..., 
                instance_close_delay_duration_in_seconds: int = ..., 
                monitoring_policy = ..., 
                rolling_upgrade_mode = "UnmonitoredAuto", 
                sort_order = "Default", 
                upgrade_kind = "Rolling", 
                upgrade_replica_set_check_timeout_in_seconds: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StartedChaosEvent(ChaosEvent):

        def __init__(
                self, 
                *, 
                chaos_parameters = ..., 
                time_stamp_utc, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.State(str, Enum):
        approved = "Approved"
        claimed = "Claimed"
        completed = "Completed"
        created = "Created"
        executing = "Executing"
        invalid = "Invalid"
        preparing = "Preparing"
        restoring = "Restoring"


    class azure.servicefabric.models.StatefulReplicaHealthReportExpiredEvent(ReplicaEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                partition_id: str, 
                property: str, 
                remove_when_expired: bool, 
                replica_id: int, 
                replica_instance_id: int, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulReplicaNewHealthReportEvent(ReplicaEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                partition_id: str, 
                property: str, 
                remove_when_expired: bool, 
                replica_id: int, 
                replica_instance_id: int, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServiceDescription(ServiceDescription):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                auxiliary_replica_count: int = ..., 
                correlation_scheme = ..., 
                default_move_cost = ..., 
                drop_source_replica_on_move: bool = ..., 
                flags: int = ..., 
                has_persisted_state: bool, 
                initialization_data = ..., 
                is_default_move_cost_specified: bool = ..., 
                min_replica_set_size: int, 
                partition_description, 
                placement_constraints: str = ..., 
                quorum_loss_wait_duration_seconds: int = ..., 
                replica_lifecycle_description = ..., 
                replica_restart_wait_duration_seconds: int = ..., 
                scaling_policies = ..., 
                service_dns_name: str = ..., 
                service_load_metrics = ..., 
                service_name: str, 
                service_package_activation_mode = ..., 
                service_placement_policies = ..., 
                service_placement_time_limit_seconds: int = ..., 
                service_type_name: str, 
                stand_by_replica_keep_duration_seconds: int = ..., 
                tags_required_to_place = ..., 
                tags_required_to_run = ..., 
                target_replica_set_size: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServiceInfo(ServiceInfo):

        def __init__(
                self, 
                *, 
                has_persisted_state: bool = ..., 
                health_state = ..., 
                id: str = ..., 
                is_service_group: bool = ..., 
                manifest_version: str = ..., 
                name: str = ..., 
                service_status = ..., 
                type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServicePartitionInfo(ServicePartitionInfo):

        def __init__(
                self, 
                *, 
                auxiliary_replica_count: int = ..., 
                health_state = ..., 
                last_quorum_loss_duration = ..., 
                min_replica_set_size: int = ..., 
                partition_information = ..., 
                partition_status = ..., 
                primary_epoch = ..., 
                target_replica_set_size: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServiceReplicaHealth(ReplicaHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                health_events = ..., 
                health_statistics = ..., 
                partition_id: str = ..., 
                replica_id: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServiceReplicaHealthState(ReplicaHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                partition_id: str = ..., 
                replica_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServiceReplicaInfo(ReplicaInfo):

        def __init__(
                self, 
                *, 
                address: str = ..., 
                health_state = ..., 
                last_in_build_duration_in_seconds: str = ..., 
                node_name: str = ..., 
                replica_id: str = ..., 
                replica_role = ..., 
                replica_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServiceTypeDescription(ServiceTypeDescription):

        def __init__(
                self, 
                *, 
                extensions = ..., 
                has_persisted_state: bool = ..., 
                is_stateful: bool = ..., 
                load_metrics = ..., 
                placement_constraints: str = ..., 
                service_placement_policies = ..., 
                service_type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatefulServiceUpdateDescription(ServiceUpdateDescription):

        def __init__(
                self, 
                *, 
                auxiliary_replica_count: int = ..., 
                correlation_scheme = ..., 
                default_move_cost = ..., 
                drop_source_replica_on_move: bool = ..., 
                flags: str = ..., 
                load_metrics = ..., 
                min_replica_set_size: int = ..., 
                placement_constraints: str = ..., 
                quorum_loss_wait_duration_seconds: str = ..., 
                replica_lifecycle_description = ..., 
                replica_restart_wait_duration_seconds: str = ..., 
                scaling_policies = ..., 
                service_dns_name: str = ..., 
                service_placement_policies = ..., 
                service_placement_time_limit_seconds: str = ..., 
                stand_by_replica_keep_duration_seconds: str = ..., 
                tags_for_placement = ..., 
                tags_for_running = ..., 
                target_replica_set_size: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessReplicaHealthReportExpiredEvent(ReplicaEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                partition_id: str, 
                property: str, 
                remove_when_expired: bool, 
                replica_id: int, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessReplicaNewHealthReportEvent(ReplicaEvent):

        def __init__(
                self, 
                *, 
                category: str = ..., 
                description: str, 
                event_instance_id: str, 
                has_correlated_events: bool = ..., 
                health_state: str, 
                partition_id: str, 
                property: str, 
                remove_when_expired: bool, 
                replica_id: int, 
                sequence_number: int, 
                source_id: str, 
                source_utc_timestamp, 
                time_stamp, 
                time_to_live_ms: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServiceDescription(ServiceDescription):

        def __init__(
                self, 
                *, 
                application_name: str = ..., 
                correlation_scheme = ..., 
                default_move_cost = ..., 
                flags: int = ..., 
                initialization_data = ..., 
                instance_close_delay_duration_seconds: int = ..., 
                instance_count: int, 
                instance_lifecycle_description = ..., 
                instance_restart_wait_duration_seconds: int = ..., 
                is_default_move_cost_specified: bool = ..., 
                min_instance_count: int = ..., 
                min_instance_percentage: int = ..., 
                partition_description, 
                placement_constraints: str = ..., 
                scaling_policies = ..., 
                service_dns_name: str = ..., 
                service_load_metrics = ..., 
                service_name: str, 
                service_package_activation_mode = ..., 
                service_placement_policies = ..., 
                service_type_name: str, 
                tags_required_to_place = ..., 
                tags_required_to_run = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServiceInfo(ServiceInfo):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                id: str = ..., 
                is_service_group: bool = ..., 
                manifest_version: str = ..., 
                name: str = ..., 
                service_status = ..., 
                type_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServiceInstanceHealth(ReplicaHealth):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                health_events = ..., 
                health_statistics = ..., 
                instance_id: str = ..., 
                partition_id: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServiceInstanceHealthState(ReplicaHealthState):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                partition_id: str = ..., 
                replica_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServiceInstanceInfo(ReplicaInfo):

        def __init__(
                self, 
                *, 
                address: str = ..., 
                health_state = ..., 
                instance_id: str = ..., 
                last_in_build_duration_in_seconds: str = ..., 
                node_name: str = ..., 
                replica_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServicePartitionInfo(ServicePartitionInfo):

        def __init__(
                self, 
                *, 
                health_state = ..., 
                instance_count: int = ..., 
                min_instance_count: int = ..., 
                min_instance_percentage: int = ..., 
                partition_information = ..., 
                partition_status = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServiceTypeDescription(ServiceTypeDescription):

        def __init__(
                self, 
                *, 
                extensions = ..., 
                is_stateful: bool = ..., 
                load_metrics = ..., 
                placement_constraints: str = ..., 
                service_placement_policies = ..., 
                service_type_name: str = ..., 
                use_implicit_host: bool = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StatelessServiceUpdateDescription(ServiceUpdateDescription):

        def __init__(
                self, 
                *, 
                correlation_scheme = ..., 
                default_move_cost = ..., 
                flags: str = ..., 
                instance_close_delay_duration_seconds: str = ..., 
                instance_count: int = ..., 
                instance_lifecycle_description = ..., 
                instance_restart_wait_duration_seconds: str = ..., 
                load_metrics = ..., 
                min_instance_count: int = ..., 
                min_instance_percentage: int = ..., 
                placement_constraints: str = ..., 
                scaling_policies = ..., 
                service_dns_name: str = ..., 
                service_placement_policies = ..., 
                tags_for_placement = ..., 
                tags_for_running = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StoppedChaosEvent(ChaosEvent):

        def __init__(
                self, 
                *, 
                reason: str = ..., 
                time_stamp_utc, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.StringPropertyValue(PropertyValue):

        def __init__(
                self, 
                *, 
                data: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SuccessfulPropertyBatchInfo(PropertyBatchInfo):

        def __init__(
                self, 
                *, 
                properties = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.SystemApplicationHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                unhealthy_evaluations = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.TcpConfig(Model):

        def __init__(
                self, 
                *, 
                destination, 
                name: str, 
                port: int, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.TestErrorChaosEvent(ChaosEvent):

        def __init__(
                self, 
                *, 
                reason: str = ..., 
                time_stamp_utc, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.TimeBasedBackupScheduleDescription(BackupScheduleDescription):

        def __init__(
                self, 
                *, 
                run_days = ..., 
                run_times, 
                schedule_frequency_type, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.TimeOfDay(Model):

        def __init__(
                self, 
                *, 
                hour: int = ..., 
                minute: int = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.TimeRange(Model):

        def __init__(
                self, 
                *, 
                end_time = ..., 
                start_time = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UniformInt64RangePartitionSchemeDescription(PartitionSchemeDescription):

        def __init__(
                self, 
                *, 
                count: int, 
                high_key: str, 
                low_key: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UnplacedReplicaInformation(Model):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                service_name: str = ..., 
                unplaced_replica_details = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UnprovisionApplicationTypeDescriptionInfo(Model):

        def __init__(
                self, 
                *, 
                application_type_version: str, 
                async_property: bool = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UnprovisionFabricDescription(Model):

        def __init__(
                self, 
                *, 
                code_version: str = ..., 
                config_version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpdateClusterUpgradeDescription(Model):

        def __init__(
                self, 
                *, 
                application_health_policy_map = ..., 
                cluster_health_policy = ..., 
                cluster_upgrade_health_policy = ..., 
                enable_delta_health_evaluation: bool = ..., 
                update_description = ..., 
                upgrade_kind = "Rolling", 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpdatePartitionLoadResult(Model):

        def __init__(
                self, 
                *, 
                partition_error_code: int = ..., 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeDomainDeltaNodesCheckHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                baseline_error_count: int = ..., 
                baseline_total_count: int = ..., 
                description: str = ..., 
                max_percent_delta_unhealthy_nodes: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                upgrade_domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeDomainDeployedApplicationsHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_deployed_applications: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                upgrade_domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeDomainInfo(Model):

        def __init__(
                self, 
                *, 
                name: str = ..., 
                state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeDomainNodesHealthEvaluation(HealthEvaluation):

        def __init__(
                self, 
                *, 
                aggregated_health_state = ..., 
                description: str = ..., 
                max_percent_unhealthy_nodes: int = ..., 
                total_count: int = ..., 
                unhealthy_evaluations = ..., 
                upgrade_domain_name: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeDomainState(str, Enum):
        completed = "Completed"
        in_progress = "InProgress"
        invalid = "Invalid"
        pending = "Pending"


    class azure.servicefabric.models.UpgradeKind(str, Enum):
        invalid = "Invalid"
        rolling = "Rolling"


    class azure.servicefabric.models.UpgradeMode(str, Enum):
        invalid = "Invalid"
        monitored = "Monitored"
        unmonitored_auto = "UnmonitoredAuto"
        unmonitored_deferred = "UnmonitoredDeferred"
        unmonitored_manual = "UnmonitoredManual"


    class azure.servicefabric.models.UpgradeOrchestrationServiceState(Model):

        def __init__(
                self, 
                *, 
                service_state: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeOrchestrationServiceStateSummary(Model):

        def __init__(
                self, 
                *, 
                current_code_version: str = ..., 
                current_manifest_version: str = ..., 
                pending_upgrade_type: str = ..., 
                target_code_version: str = ..., 
                target_manifest_version: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeSortOrder(str, Enum):
        default = "Default"
        invalid = "Invalid"
        lexicographical = "Lexicographical"
        numeric = "Numeric"
        reverse_lexicographical = "ReverseLexicographical"
        reverse_numeric = "ReverseNumeric"


    class azure.servicefabric.models.UpgradeState(str, Enum):
        failed = "Failed"
        invalid = "Invalid"
        rolling_back_completed = "RollingBackCompleted"
        rolling_back_in_progress = "RollingBackInProgress"
        rolling_forward_completed = "RollingForwardCompleted"
        rolling_forward_in_progress = "RollingForwardInProgress"
        rolling_forward_pending = "RollingForwardPending"


    class azure.servicefabric.models.UpgradeType(str, Enum):
        invalid = "Invalid"
        rolling = "Rolling"
        rolling_force_restart = "Rolling_ForceRestart"


    class azure.servicefabric.models.UpgradeUnitInfo(Model):

        def __init__(
                self, 
                *, 
                name: str = ..., 
                state = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UpgradeUnitState(str, Enum):
        completed = "Completed"
        failed = "Failed"
        in_progress = "InProgress"
        invalid = "Invalid"
        pending = "Pending"


    class azure.servicefabric.models.UploadChunkRange(Model):

        def __init__(
                self, 
                *, 
                end_position: str = ..., 
                start_position: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UploadSession(Model):

        def __init__(
                self, 
                *, 
                upload_sessions = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UploadSessionInfo(Model):

        def __init__(
                self, 
                *, 
                expected_ranges = ..., 
                file_size: str = ..., 
                modified_date = ..., 
                session_id: str = ..., 
                store_relative_path: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.UsageInfo(Model):

        def __init__(
                self, 
                *, 
                file_count: str = ..., 
                used_space: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ValidateClusterUpgradeResult(Model):

        def __init__(
                self, 
                *, 
                service_host_upgrade_impact = ..., 
                validation_details: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.ValidationFailedChaosEvent(ChaosEvent):

        def __init__(
                self, 
                *, 
                reason: str = ..., 
                time_stamp_utc, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.VolumeProvider(str, Enum):
        sf_azure_file = "SFAzureFile"


    class azure.servicefabric.models.VolumeProviderParametersAzureFile(Model):

        def __init__(
                self, 
                *, 
                account_key: str = ..., 
                account_name: str, 
                share_name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.VolumeReference(Model):

        def __init__(
                self, 
                *, 
                destination_path: str, 
                name: str, 
                read_only: bool = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.VolumeResourceDescription(Model):
        provider: str = "SFAzureFile"
        status: Union[str, ResourceStatus]
        status_details: str

        def __init__(
                self, 
                *, 
                azure_file_parameters = ..., 
                description: str = ..., 
                name: str, 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.WaitForInbuildReplicaSafetyCheck(PartitionSafetyCheck):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.WaitForPrimaryPlacementSafetyCheck(PartitionSafetyCheck):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.WaitForPrimarySwapSafetyCheck(PartitionSafetyCheck):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.WaitForReconfigurationSafetyCheck(PartitionSafetyCheck):

        def __init__(
                self, 
                *, 
                partition_id: str = ..., 
                **kwargs
            ) -> None: ...


    class azure.servicefabric.models.WaitingChaosEvent(ChaosEvent):

        def __init__(
                self, 
                *, 
                reason: str = ..., 
                time_stamp_utc, 
                **kwargs
            ) -> None: ...


namespace azure.servicefabric.operations

    class azure.servicefabric.operations.MeshApplicationOperations:

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                application_resource_name: str, 
                application_resource_description: ApplicationResourceDescription, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationResourceDescription, ClientRawResponse]: ...

        def delete(
                self, 
                application_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get(
                self, 
                application_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationResourceDescription, ClientRawResponse]: ...

        def get_upgrade_progress(
                self, 
                application_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> ApplicationResourceUpgradeProgressInfo or: ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedApplicationResourceDescriptionList or: ...


    class azure.servicefabric.operations.MeshCodePackageOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get_container_logs(
                self, 
                application_resource_name: str, 
                service_resource_name: str, 
                replica_name: str, 
                code_package_name: str, 
                tail: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ContainerLogs, ClientRawResponse]: ...


    class azure.servicefabric.operations.MeshGatewayOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                gateway_resource_name: str, 
                gateway_resource_description: GatewayResourceDescription, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[GatewayResourceDescription, ClientRawResponse]: ...

        def delete(
                self, 
                gateway_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get(
                self, 
                gateway_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[GatewayResourceDescription, ClientRawResponse]: ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedGatewayResourceDescriptionList or: ...


    class azure.servicefabric.operations.MeshNetworkOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                network_resource_name: str, 
                name: str, 
                properties: NetworkResourceProperties, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NetworkResourceDescription, ClientRawResponse]: ...

        def delete(
                self, 
                network_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get(
                self, 
                network_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NetworkResourceDescription, ClientRawResponse]: ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedNetworkResourceDescriptionList or: ...


    class azure.servicefabric.operations.MeshSecretOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                secret_resource_name: str, 
                properties: SecretResourceProperties, 
                name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[SecretResourceDescription, ClientRawResponse]: ...

        def delete(
                self, 
                secret_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get(
                self, 
                secret_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[SecretResourceDescription, ClientRawResponse]: ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedSecretResourceDescriptionList: ...


    class azure.servicefabric.operations.MeshSecretValueOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def add_value(
                self, 
                secret_resource_name: str, 
                secret_value_resource_name: str, 
                name: str, 
                value: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[SecretValueResourceDescription, ClientRawResponse]: ...

        def delete(
                self, 
                secret_resource_name: str, 
                secret_value_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get(
                self, 
                secret_resource_name: str, 
                secret_value_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[SecretValueResourceDescription, ClientRawResponse]: ...

        def list(
                self, 
                secret_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedSecretValueResourceDescriptionList or: ...

        def show(
                self, 
                secret_resource_name: str, 
                secret_value_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[SecretValue, ClientRawResponse]: ...


    class azure.servicefabric.operations.MeshServiceOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                application_resource_name: str, 
                service_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceResourceDescription, ClientRawResponse]: ...

        def list(
                self, 
                application_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedServiceResourceDescriptionList or: ...


    class azure.servicefabric.operations.MeshServiceReplicaOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def get(
                self, 
                application_resource_name: str, 
                service_resource_name: str, 
                replica_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceReplicaDescription, ClientRawResponse]: ...

        def list(
                self, 
                application_resource_name: str, 
                service_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedServiceReplicaDescriptionList: ...


    class azure.servicefabric.operations.MeshVolumeOperations:
        api_version

        def __init__(
                self, 
                client, 
                config, 
                serializer, 
                deserializer
            ): ...

        def create_or_update(
                self, 
                volume_resource_name: str, 
                volume_resource_description: VolumeResourceDescription, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[VolumeResourceDescription, ClientRawResponse]: ...

        def delete(
                self, 
                volume_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get(
                self, 
                volume_resource_name: str, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[VolumeResourceDescription, ClientRawResponse]: ...

        def list(
                self, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedVolumeResourceDescriptionList: ...


    class azure.servicefabric.operations.ServiceFabricClientAPIsOperationsMixin:

        def add_configuration_parameter_overrides(
                self, 
                node_name: str, 
                config_parameter_override_list: list[ConfigParameterOverride], 
                force: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def add_node_tags(
                self, 
                node_name: str, 
                node_tags: list[str], 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def backup_partition(
                self, 
                partition_id: str, 
                backup_timeout: int = 10, 
                timeout: long = 60, 
                backup_storage: BackupStorageDescription = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def cancel_operation(
                self, 
                operation_id: str, 
                force: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def cancel_repair_task(
                self, 
                repair_task_cancel_description: RepairTaskCancelDescription, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def commit_image_store_upload_session(
                self, 
                session_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def copy_image_store_content(
                self, 
                image_store_copy_description: ImageStoreCopyDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_application(
                self, 
                application_description: ApplicationDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_backup_policy(
                self, 
                backup_policy_description: BackupPolicyDescription, 
                timeout: long = 60, 
                validate_connection: bool = False, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_compose_deployment(
                self, 
                create_compose_deployment_description: CreateComposeDeploymentDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_name(
                self, 
                name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_repair_task(
                self, 
                repair_task: RepairTask, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def create_service(
                self, 
                application_id: str, 
                service_description: ServiceDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def create_service_from_template(
                self, 
                application_id: str, 
                service_from_template_description: ServiceFromTemplateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_application(
                self, 
                application_id: str, 
                force_remove: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_backup_policy(
                self, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_image_store_content(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_image_store_upload_session(
                self, 
                session_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_name(
                self, 
                name_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_property(
                self, 
                name_id: str, 
                property_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_repair_task(
                self, 
                task_id: str, 
                version: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def delete_service(
                self, 
                service_id: str, 
                force_remove: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def deploy_service_package_to_node(
                self, 
                node_name: str, 
                deploy_service_package_to_node_description: DeployServicePackageToNodeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_application_backup(
                self, 
                application_id: str, 
                clean_backup: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_node(
                self, 
                node_name: str, 
                timeout: long = 60, 
                deactivation_intent: Union[str, DeactivationIntent] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_partition_backup(
                self, 
                partition_id: str, 
                clean_backup: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def disable_service_backup(
                self, 
                service_id: str, 
                clean_backup: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_application_backup(
                self, 
                application_id: str, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_node(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_partition_backup(
                self, 
                partition_id: str, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def enable_service_backup(
                self, 
                service_id: str, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def force_approve_repair_task(
                self, 
                task_id: str, 
                version: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def get_aad_metadata(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[AadMetadataObject, ClientRawResponse]: ...

        def get_all_entities_backed_up_by_policy(
                self, 
                backup_policy_name: str, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupEntityList, ClientRawResponse]: ...

        def get_application_backup_configuration_info(
                self, 
                application_id: str, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedBackupConfigurationInfoList: ...

        def get_application_backup_list(
                self, 
                application_id: str, 
                timeout: long = 60, 
                latest: bool = False, 
                start_date_time_filter: datetime = None, 
                end_date_time_filter: datetime = None, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_application_event_list(
                self, 
                application_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ApplicationEvent], ClientRawResponse]: ...

        def get_application_health(
                self, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_applications_health_state_filter: int = 0, 
                services_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationHealth, ClientRawResponse]: ...

        def get_application_health_using_policy(
                self, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_applications_health_state_filter: int = 0, 
                services_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                application_health_policy: ApplicationHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationHealth, ClientRawResponse]: ...

        def get_application_info(
                self, 
                application_id: str, 
                exclude_application_parameters: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationInfo, ClientRawResponse]: ...

        def get_application_info_list(
                self, 
                application_definition_kind_filter: int = 0, 
                application_type_name: str = None, 
                exclude_application_parameters: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedApplicationInfoList, ClientRawResponse]: ...

        def get_application_load_info(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationLoadInfo, ClientRawResponse]: ...

        def get_application_manifest(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationTypeManifest, ClientRawResponse]: ...

        def get_application_name_info(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationNameInfo, ClientRawResponse]: ...

        def get_application_type_info_list(
                self, 
                application_type_definition_kind_filter: int = 0, 
                exclude_application_parameters: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedApplicationTypeInfoList, ClientRawResponse]: ...

        def get_application_type_info_list_by_name(
                self, 
                application_type_name: str, 
                application_type_version: str = None, 
                exclude_application_parameters: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedApplicationTypeInfoList, ClientRawResponse]: ...

        def get_application_upgrade(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ApplicationUpgradeProgressInfo, ClientRawResponse]: ...

        def get_applications_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ApplicationEvent], ClientRawResponse]: ...

        def get_backup_policy_by_name(
                self, 
                backup_policy_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[BackupPolicyDescription, ClientRawResponse]: ...

        def get_backup_policy_list(
                self, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedBackupPolicyDescriptionList: ...

        def get_backups_from_backup_location(
                self, 
                get_backup_by_storage_query_description: GetBackupByStorageQueryDescription, 
                timeout: long = 60, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_chaos(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[Chaos, ClientRawResponse]: ...

        def get_chaos_events(
                self, 
                continuation_token: str = None, 
                start_time_utc: str = None, 
                end_time_utc: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ChaosEventsSegment, ClientRawResponse]: ...

        def get_chaos_schedule(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ChaosScheduleDescription, ClientRawResponse]: ...

        def get_cluster_configuration(
                self, 
                configuration_api_version: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterConfiguration, ClientRawResponse]: ...

        def get_cluster_configuration_upgrade_status(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> ClusterConfigurationUpgradeStatusInfo or: ...

        def get_cluster_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ClusterEvent], ClientRawResponse]: ...

        def get_cluster_health(
                self, 
                nodes_health_state_filter: int = 0, 
                applications_health_state_filter: int = 0, 
                events_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                include_system_application_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealth, ClientRawResponse]: ...

        def get_cluster_health_chunk(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealthChunk, ClientRawResponse]: ...

        def get_cluster_health_chunk_using_policy_and_advanced_filters(
                self, 
                cluster_health_chunk_query_description: ClusterHealthChunkQueryDescription = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealthChunk, ClientRawResponse]: ...

        def get_cluster_health_using_policy(
                self, 
                nodes_health_state_filter: int = 0, 
                applications_health_state_filter: int = 0, 
                events_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                include_system_application_health_statistics: bool = False, 
                timeout: long = 60, 
                application_health_policy_map: list[ApplicationHealthPolicyMapItem] = None, 
                cluster_health_policy: ClusterHealthPolicy = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterHealth, ClientRawResponse]: ...

        def get_cluster_load(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterLoadInfo, ClientRawResponse]: ...

        def get_cluster_manifest(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterManifest, ClientRawResponse]: ...

        def get_cluster_upgrade_progress(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterUpgradeProgressObject, ClientRawResponse]: ...

        def get_cluster_version(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ClusterVersion, ClientRawResponse]: ...

        def get_compose_deployment_status(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ComposeDeploymentStatusInfo, ClientRawResponse]: ...

        def get_compose_deployment_status_list(
                self, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedComposeDeploymentStatusInfoList or: ...

        def get_compose_deployment_upgrade_progress(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> ComposeDeploymentUpgradeProgressInfo or: ...

        def get_configuration_overrides(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ConfigParameterOverride], ClientRawResponse]: ...

        def get_container_logs_deployed_on_node(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str, 
                code_package_name: str, 
                tail: str = None, 
                previous: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ContainerLogs, ClientRawResponse]: ...

        def get_containers_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ContainerInstanceEvent], ClientRawResponse]: ...

        def get_correlated_event_list(
                self, 
                event_instance_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[FabricEvent], ClientRawResponse]: ...

        def get_data_loss_progress(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionDataLossProgress, ClientRawResponse]: ...

        def get_deployed_application_health(
                self, 
                node_name: str, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_service_packages_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedApplicationHealth, ClientRawResponse]: ...

        def get_deployed_application_health_using_policy(
                self, 
                node_name: str, 
                application_id: str, 
                events_health_state_filter: int = 0, 
                deployed_service_packages_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedApplicationHealth, ClientRawResponse]: ...

        def get_deployed_application_info(
                self, 
                node_name: str, 
                application_id: str, 
                timeout: long = 60, 
                include_health_state: bool = False, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedApplicationInfo, ClientRawResponse]: ...

        def get_deployed_application_info_list(
                self, 
                node_name: str, 
                timeout: long = 60, 
                include_health_state: bool = False, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedDeployedApplicationInfoList: ...

        def get_deployed_code_package_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str = None, 
                code_package_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[DeployedCodePackageInfo], ClientRawResponse]: ...

        def get_deployed_service_package_health(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                events_health_state_filter: int = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedServicePackageHealth, ClientRawResponse]: ...

        def get_deployed_service_package_health_using_policy(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                events_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[DeployedServicePackageHealth, ClientRawResponse]: ...

        def get_deployed_service_package_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> list[DeployedServicePackageInfo]: ...

        def get_deployed_service_package_info_list_by_name(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> list[DeployedServicePackageInfo]: ...

        def get_deployed_service_replica_detail_info(
                self, 
                node_name: str, 
                partition_id: str, 
                replica_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DeployedServiceReplicaDetailInfo: ...

        def get_deployed_service_replica_detail_info_by_partition_id(
                self, 
                node_name: str, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> DeployedServiceReplicaDetailInfo: ...

        def get_deployed_service_replica_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                partition_id: str = None, 
                service_manifest_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> list[DeployedServiceReplicaInfo]: ...

        def get_deployed_service_type_info_by_name(
                self, 
                node_name: str, 
                application_id: str, 
                service_type_name: str, 
                service_manifest_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[DeployedServiceTypeInfo], ClientRawResponse]: ...

        def get_deployed_service_type_info_list(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[DeployedServiceTypeInfo], ClientRawResponse]: ...

        def get_fault_operation_list(
                self, 
                type_filter: int = 65535, 
                state_filter: int = 65535, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[OperationStatus], ClientRawResponse]: ...

        def get_image_store_content(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ImageStoreContent, ClientRawResponse]: ...

        def get_image_store_folder_size(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[FolderSizeInfo, ClientRawResponse]: ...

        def get_image_store_info(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ImageStoreInfo, ClientRawResponse]: ...

        def get_image_store_root_content(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ImageStoreContent, ClientRawResponse]: ...

        def get_image_store_root_folder_size(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[FolderSizeInfo, ClientRawResponse]: ...

        def get_image_store_upload_session_by_id(
                self, 
                session_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UploadSession, ClientRawResponse]: ...

        def get_image_store_upload_session_by_path(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UploadSession, ClientRawResponse]: ...

        def get_loaded_partition_info_list(
                self, 
                metric_name: str, 
                service_name: str = None, 
                ordering: Union[str, Ordering] = "Desc", 
                max_results: long = 0, 
                continuation_token: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> LoadedPartitionInformationResultList or: ...

        def get_name_exists_info(
                self, 
                name_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def get_node_event_list(
                self, 
                node_name: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[NodeEvent], ClientRawResponse]: ...

        def get_node_health(
                self, 
                node_name: str, 
                events_health_state_filter: int = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeHealth, ClientRawResponse]: ...

        def get_node_health_using_policy(
                self, 
                node_name: str, 
                events_health_state_filter: int = 0, 
                cluster_health_policy: ClusterHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeHealth, ClientRawResponse]: ...

        def get_node_info(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeInfo, ClientRawResponse]: ...

        def get_node_info_list(
                self, 
                continuation_token: str = None, 
                node_status_filter: Union[str, NodeStatusFilter] = "default", 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedNodeInfoList, ClientRawResponse]: ...

        def get_node_load_info(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeLoadInfo, ClientRawResponse]: ...

        def get_node_transition_progress(
                self, 
                node_name: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[NodeTransitionProgress, ClientRawResponse]: ...

        def get_nodes_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[NodeEvent], ClientRawResponse]: ...

        def get_partition_backup_configuration_info(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PartitionBackupConfigurationInfo: ...

        def get_partition_backup_list(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                latest: bool = False, 
                start_date_time_filter: datetime = None, 
                end_date_time_filter: datetime = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_partition_backup_progress(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[BackupProgressInfo, ClientRawResponse]: ...

        def get_partition_event_list(
                self, 
                partition_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[PartitionEvent], ClientRawResponse]: ...

        def get_partition_health(
                self, 
                partition_id: str, 
                events_health_state_filter: int = 0, 
                replicas_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionHealth, ClientRawResponse]: ...

        def get_partition_health_using_policy(
                self, 
                partition_id: str, 
                events_health_state_filter: int = 0, 
                replicas_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionHealth, ClientRawResponse]: ...

        def get_partition_info(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServicePartitionInfo, ClientRawResponse]: ...

        def get_partition_info_list(
                self, 
                service_id: str, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedServicePartitionInfoList, ClientRawResponse]: ...

        def get_partition_load_information(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionLoadInformation, ClientRawResponse]: ...

        def get_partition_replica_event_list(
                self, 
                partition_id: str, 
                replica_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ReplicaEvent], ClientRawResponse]: ...

        def get_partition_replicas_event_list(
                self, 
                partition_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ReplicaEvent], ClientRawResponse]: ...

        def get_partition_restart_progress(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionRestartProgress, ClientRawResponse]: ...

        def get_partition_restore_progress(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RestoreProgressInfo, ClientRawResponse]: ...

        def get_partitions_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[PartitionEvent], ClientRawResponse]: ...

        def get_property_info(
                self, 
                name_id: str, 
                property_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PropertyInfo, ClientRawResponse]: ...

        def get_property_info_list(
                self, 
                name_id: str, 
                include_values: bool = False, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedPropertyInfoList, ClientRawResponse]: ...

        def get_provisioned_fabric_code_version_info_list(
                self, 
                code_version: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[FabricCodeVersionInfo], ClientRawResponse]: ...

        def get_provisioned_fabric_config_version_info_list(
                self, 
                config_version: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[FabricConfigVersionInfo], ClientRawResponse]: ...

        def get_quorum_loss_progress(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PartitionQuorumLossProgress, ClientRawResponse]: ...

        def get_repair_task_list(
                self, 
                task_id_filter: str = None, 
                state_filter: int = None, 
                executor_filter: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[RepairTask], ClientRawResponse]: ...

        def get_replica_health(
                self, 
                partition_id: str, 
                replica_id: str, 
                events_health_state_filter: int = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ReplicaHealth, ClientRawResponse]: ...

        def get_replica_health_using_policy(
                self, 
                partition_id: str, 
                replica_id: str, 
                events_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ReplicaHealth, ClientRawResponse]: ...

        def get_replica_info(
                self, 
                partition_id: str, 
                replica_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ReplicaInfo, ClientRawResponse]: ...

        def get_replica_info_list(
                self, 
                partition_id: str, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedReplicaInfoList, ClientRawResponse]: ...

        def get_service_backup_configuration_info(
                self, 
                service_id: str, 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedBackupConfigurationInfoList: ...

        def get_service_backup_list(
                self, 
                service_id: str, 
                timeout: long = 60, 
                latest: bool = False, 
                start_date_time_filter: datetime = None, 
                end_date_time_filter: datetime = None, 
                continuation_token: str = None, 
                max_results: long = 0, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedBackupInfoList, ClientRawResponse]: ...

        def get_service_description(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceDescription, ClientRawResponse]: ...

        def get_service_event_list(
                self, 
                service_id: str, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ServiceEvent], ClientRawResponse]: ...

        def get_service_health(
                self, 
                service_id: str, 
                events_health_state_filter: int = 0, 
                partitions_health_state_filter: int = 0, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceHealth, ClientRawResponse]: ...

        def get_service_health_using_policy(
                self, 
                service_id: str, 
                events_health_state_filter: int = 0, 
                partitions_health_state_filter: int = 0, 
                application_health_policy: ApplicationHealthPolicy = None, 
                exclude_health_statistics: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceHealth, ClientRawResponse]: ...

        def get_service_info(
                self, 
                application_id: str, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceInfo, ClientRawResponse]: ...

        def get_service_info_list(
                self, 
                application_id: str, 
                service_type_name: str = None, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedServiceInfoList, ClientRawResponse]: ...

        def get_service_manifest(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                service_manifest_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceTypeManifest, ClientRawResponse]: ...

        def get_service_name_info(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceNameInfo, ClientRawResponse]: ...

        def get_service_type_info_by_name(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                service_type_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ServiceTypeInfo, ClientRawResponse]: ...

        def get_service_type_info_list(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ServiceTypeInfo], ClientRawResponse]: ...

        def get_services_event_list(
                self, 
                start_time_utc: str, 
                end_time_utc: str, 
                timeout: long = 60, 
                events_types_filter: str = None, 
                exclude_analysis_events: bool = None, 
                skip_correlation_lookup: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[list[ServiceEvent], ClientRawResponse]: ...

        def get_sub_name_info_list(
                self, 
                name_id: str, 
                recursive: bool = False, 
                continuation_token: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PagedSubNameInfoList, ClientRawResponse]: ...

        def get_unplaced_replica_information(
                self, 
                service_id: str, 
                partition_id: str = None, 
                only_query_primaries: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[UnplacedReplicaInformation, ClientRawResponse]: ...

        def get_upgrade_orchestration_service_state(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> UpgradeOrchestrationServiceState: ...

        def invoke_container_api(
                self, 
                node_name: str, 
                application_id: str, 
                service_manifest_name: str, 
                code_package_name: str, 
                code_package_instance_id: str, 
                container_api_request_body: ContainerApiRequestBody, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ContainerApiResponse, ClientRawResponse]: ...

        def invoke_infrastructure_command(
                self, 
                command: str, 
                service_id: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[str, ClientRawResponse]: ...

        def invoke_infrastructure_query(
                self, 
                command: str, 
                service_id: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[str, ClientRawResponse]: ...

        def move_auxiliary_replica(
                self, 
                service_id: str, 
                partition_id: str, 
                current_node_name: str = None, 
                new_node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def move_instance(
                self, 
                service_id: str, 
                partition_id: str, 
                current_node_name: str = None, 
                new_node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def move_primary_replica(
                self, 
                partition_id: str, 
                node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def move_secondary_replica(
                self, 
                partition_id: str, 
                current_node_name: str, 
                new_node_name: str = None, 
                ignore_constraints: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def post_chaos_schedule(
                self, 
                timeout: long = 60, 
                version: int = None, 
                schedule: ChaosSchedule = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def provision_application_type(
                self, 
                provision_application_type_description_base_required_body_param, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def provision_cluster(
                self, 
                timeout: long = 60, 
                code_file_path: str = None, 
                cluster_manifest_file_path: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def put_property(
                self, 
                name_id: str, 
                property_description: PropertyDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_all_partitions(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_partition(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_service_partitions(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def recover_system_partitions(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_compose_deployment(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_configuration_overrides(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_node_state(
                self, 
                node_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_node_tags(
                self, 
                node_name: str, 
                node_tags: list[str], 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def remove_replica(
                self, 
                node_name: str, 
                partition_id: str, 
                replica_id: str, 
                force_remove: bool = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_application_health(
                self, 
                application_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_cluster_health(
                self, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_deployed_application_health(
                self, 
                node_name: str, 
                application_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_deployed_service_package_health(
                self, 
                node_name: str, 
                application_id: str, 
                service_package_name: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_node_health(
                self, 
                node_name: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_partition_health(
                self, 
                partition_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_replica_health(
                self, 
                partition_id: str, 
                replica_id: str, 
                health_information: HealthInformation, 
                service_kind: Union[str, ReplicaHealthReportServiceKind] = "Stateful", 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def report_service_health(
                self, 
                service_id: str, 
                health_information: HealthInformation, 
                immediate: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def reset_partition_load(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resolve_service(
                self, 
                service_id: str, 
                partition_key_type: int = None, 
                partition_key_value: str = None, 
                previous_rsp_version: str = None, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ResolvedServicePartition, ClientRawResponse]: ...

        def restart_deployed_code_package(
                self, 
                node_name: str, 
                application_id: str, 
                restart_deployed_code_package_description: RestartDeployedCodePackageDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def restart_node(
                self, 
                node_name: str, 
                node_instance_id: str = "0", 
                timeout: long = 60, 
                create_fabric_dump: Union[str, CreateFabricDump] = "False", 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def restart_replica(
                self, 
                node_name: str, 
                partition_id: str, 
                replica_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def restore_partition(
                self, 
                partition_id: str, 
                restore_partition_description: RestorePartitionDescription, 
                restore_timeout: int = 10, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_application_backup(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_application_upgrade(
                self, 
                application_id: str, 
                upgrade_domain_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_cluster_upgrade(
                self, 
                upgrade_domain: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_partition_backup(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def resume_service_backup(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def rollback_application_upgrade(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def rollback_cluster_upgrade(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def set_upgrade_orchestration_service_state(
                self, 
                timeout: long = 60, 
                service_state: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> UpgradeOrchestrationServiceStateSummary or: ...

        def start_application_upgrade(
                self, 
                application_id: str, 
                application_upgrade_description: ApplicationUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_chaos(
                self, 
                chaos_parameters: ChaosParameters, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_cluster_configuration_upgrade(
                self, 
                cluster_configuration_upgrade_description: ClusterConfigurationUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_cluster_upgrade(
                self, 
                start_cluster_upgrade_description: StartClusterUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_compose_deployment_upgrade(
                self, 
                deployment_name: str, 
                compose_deployment_upgrade_description: ComposeDeploymentUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_data_loss(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                data_loss_mode: Union[str, DataLossMode], 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_node_transition(
                self, 
                node_name: str, 
                operation_id: str, 
                node_transition_type: Union[str, NodeTransitionType], 
                node_instance_id: str, 
                stop_duration_in_seconds: int, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_partition_restart(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                restart_partition_mode: Union[str, RestartPartitionMode], 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_quorum_loss(
                self, 
                service_id: str, 
                partition_id: str, 
                operation_id: str, 
                quorum_loss_mode: Union[str, QuorumLossMode], 
                quorum_loss_duration: int, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def start_rollback_compose_deployment_upgrade(
                self, 
                deployment_name: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def stop_chaos(
                self, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def submit_property_batch(
                self, 
                name_id: str, 
                timeout: long = 60, 
                operations: list[PropertyBatchOperation] = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[PropertyBatchInfo, ClientRawResponse]: ...

        def suspend_application_backup(
                self, 
                application_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def suspend_partition_backup(
                self, 
                partition_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def suspend_service_backup(
                self, 
                service_id: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def toggle_verbose_service_placement_health_reporting(
                self, 
                enabled: bool = False, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def unprovision_application_type(
                self, 
                application_type_name: str, 
                application_type_version: str, 
                timeout: long = 60, 
                async_parameter: bool = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def unprovision_cluster(
                self, 
                timeout: long = 60, 
                code_version: str = None, 
                config_version: str = None, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_application(
                self, 
                application_id: str, 
                application_update_description: ApplicationUpdateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_application_upgrade(
                self, 
                application_id: str, 
                application_upgrade_update_description: ApplicationUpgradeUpdateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_backup_policy(
                self, 
                backup_policy_description: BackupPolicyDescription, 
                backup_policy_name: str, 
                timeout: long = 60, 
                validate_connection: bool = False, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_cluster_upgrade(
                self, 
                update_cluster_upgrade_description: UpdateClusterUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def update_partition_load(
                self, 
                partition_metric_load_description_list: list[PartitionMetricLoadDescription], 
                continuation_token: str = None, 
                max_results: long = 0, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> PagedUpdatePartitionLoadResultList: ...

        def update_repair_execution_state(
                self, 
                repair_task: RepairTask, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def update_repair_task_health_policy(
                self, 
                repair_task_update_health_policy_description: RepairTaskUpdateHealthPolicyDescription, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[RepairTaskUpdateInfo, ClientRawResponse]: ...

        def update_service(
                self, 
                service_id: str, 
                service_update_description: ServiceUpdateDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def upload_file(
                self, 
                content_path: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def upload_file_chunk(
                self, 
                content_path: str, 
                session_id: str, 
                content_range: str, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[None, ClientRawResponse]: ...

        def validate_cluster_upgrade(
                self, 
                start_cluster_upgrade_description: StartClusterUpgradeDescription, 
                timeout: long = 60, 
                custom_headers: dict = None, 
                raw: bool = False, 
                **operation_config
            ) -> Union[ValidateClusterUpgradeResult, ClientRawResponse]: ...


```