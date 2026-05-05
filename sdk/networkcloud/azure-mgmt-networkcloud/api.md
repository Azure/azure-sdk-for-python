```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.networkcloud

    class azure.mgmt.networkcloud.NetworkCloudMgmtClient: implements ContextManager 
        agent_pools: AgentPoolsOperations
        bare_metal_machine_key_sets: BareMetalMachineKeySetsOperations
        bare_metal_machines: BareMetalMachinesOperations
        bmc_key_sets: BmcKeySetsOperations
        cloud_services_networks: CloudServicesNetworksOperations
        cluster_managers: ClusterManagersOperations
        clusters: ClustersOperations
        consoles: ConsolesOperations
        kubernetes_cluster_features: KubernetesClusterFeaturesOperations
        kubernetes_clusters: KubernetesClustersOperations
        l2_networks: L2NetworksOperations
        l3_networks: L3NetworksOperations
        metrics_configurations: MetricsConfigurationsOperations
        operations: Operations
        rack_skus: RackSkusOperations
        racks: RacksOperations
        storage_appliances: StorageAppliancesOperations
        trunked_networks: TrunkedNetworksOperations
        virtual_machines: VirtualMachinesOperations
        volumes: VolumesOperations

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


namespace azure.mgmt.networkcloud.aio

    class azure.mgmt.networkcloud.aio.NetworkCloudMgmtClient: implements AsyncContextManager 
        agent_pools: AgentPoolsOperations
        bare_metal_machine_key_sets: BareMetalMachineKeySetsOperations
        bare_metal_machines: BareMetalMachinesOperations
        bmc_key_sets: BmcKeySetsOperations
        cloud_services_networks: CloudServicesNetworksOperations
        cluster_managers: ClusterManagersOperations
        clusters: ClustersOperations
        consoles: ConsolesOperations
        kubernetes_cluster_features: KubernetesClusterFeaturesOperations
        kubernetes_clusters: KubernetesClustersOperations
        l2_networks: L2NetworksOperations
        l3_networks: L3NetworksOperations
        metrics_configurations: MetricsConfigurationsOperations
        operations: Operations
        rack_skus: RackSkusOperations
        racks: RacksOperations
        storage_appliances: StorageAppliancesOperations
        trunked_networks: TrunkedNetworksOperations
        virtual_machines: VirtualMachinesOperations
        volumes: VolumesOperations

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


namespace azure.mgmt.networkcloud.aio.operations

    class azure.mgmt.networkcloud.aio.operations.AgentPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_parameters: AgentPool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_update_parameters: Optional[AgentPoolPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentPool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPool: ...

        @distributed_trace
        def list_by_kubernetes_cluster(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentPool]: ...


    class azure.mgmt.networkcloud.aio.operations.BareMetalMachineKeySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_parameters: BareMetalMachineKeySet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachineKeySet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachineKeySet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachineKeySet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_update_parameters: Optional[BareMetalMachineKeySetPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachineKeySet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachineKeySet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachineKeySet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                **kwargs: Any
            ) -> BareMetalMachineKeySet: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BareMetalMachineKeySet]: ...


    class azure.mgmt.networkcloud.aio.operations.BareMetalMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_cordon_parameters: Optional[BareMetalMachineCordonParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_cordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_cordon_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_cordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_cordon_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_parameters: BareMetalMachine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachine]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_power_off_parameters: Optional[BareMetalMachinePowerOffParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_power_off_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_power_off_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_replace(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_replace_parameters: Optional[BareMetalMachineReplaceParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_replace(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_replace_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_replace(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_replace_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_command_parameters: BareMetalMachineRunCommandParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_command_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_command_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_data_extracts(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_parameters: BareMetalMachineRunDataExtractsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_data_extracts(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_data_extracts(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_data_extracts_restricted(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_restricted_parameters: BareMetalMachineRunDataExtractsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_data_extracts_restricted(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_restricted_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_data_extracts_restricted(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_restricted_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_read_commands_parameters: BareMetalMachineRunReadCommandsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_read_commands_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_read_commands_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_uncordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_update_parameters: Optional[BareMetalMachinePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BareMetalMachine]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> BareMetalMachine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BareMetalMachine]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BareMetalMachine]: ...


    class azure.mgmt.networkcloud.aio.operations.BmcKeySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_parameters: BmcKeySet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BmcKeySet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BmcKeySet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BmcKeySet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_update_parameters: Optional[BmcKeySetPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BmcKeySet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BmcKeySet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[BmcKeySet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                **kwargs: Any
            ) -> BmcKeySet: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[BmcKeySet]: ...


    class azure.mgmt.networkcloud.aio.operations.CloudServicesNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_parameters: CloudServicesNetwork, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudServicesNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudServicesNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudServicesNetwork]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_update_parameters: Optional[CloudServicesNetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudServicesNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudServicesNetwork]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudServicesNetwork]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                **kwargs: Any
            ) -> CloudServicesNetwork: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudServicesNetwork]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudServicesNetwork]: ...


    class azure.mgmt.networkcloud.aio.operations.ClusterManagersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_parameters: ClusterManager, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterManager]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterManager]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterManager]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                **kwargs: Any
            ) -> ClusterManager: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterManager]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterManager]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_update_parameters: Optional[ClusterManagerPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClusterManager: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClusterManager: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClusterManager: ...


    class azure.mgmt.networkcloud.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_continue_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_continue_update_version_parameters: ClusterContinueUpdateVersionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_continue_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_continue_update_version_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_continue_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_continue_update_version_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_deploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_deploy_parameters: Optional[ClusterDeployParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_deploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_deploy_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_deploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_deploy_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_scan_runtime(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_scan_runtime_parameters: Optional[ClusterScanRuntimeParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_scan_runtime(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_scan_runtime_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_scan_runtime(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_scan_runtime_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_parameters: Optional[ClusterPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_version_parameters: ClusterUpdateVersionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_version_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_version_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...


    class azure.mgmt.networkcloud.aio.operations.ConsolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_parameters: Console, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Console]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Console]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Console]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_update_parameters: Optional[ConsolePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Console]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Console]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Console]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                **kwargs: Any
            ) -> Console: ...

        @distributed_trace
        def list_by_virtual_machine(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Console]: ...


    class azure.mgmt.networkcloud.aio.operations.KubernetesClusterFeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_parameters: KubernetesClusterFeature, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesClusterFeature]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesClusterFeature]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesClusterFeature]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_update_parameters: Optional[KubernetesClusterFeaturePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesClusterFeature]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesClusterFeature]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesClusterFeature]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> KubernetesClusterFeature: ...

        @distributed_trace
        def list_by_kubernetes_cluster(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[KubernetesClusterFeature]: ...


    class azure.mgmt.networkcloud.aio.operations.KubernetesClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_parameters: KubernetesCluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_restart_node(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_restart_node_parameters: KubernetesClusterRestartNodeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_restart_node(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_restart_node_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_restart_node(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_restart_node_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_update_parameters: Optional[KubernetesClusterPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesCluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[KubernetesCluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                **kwargs: Any
            ) -> KubernetesCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[KubernetesCluster]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[KubernetesCluster]: ...


    class azure.mgmt.networkcloud.aio.operations.L2NetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_parameters: L2Network, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[L2Network]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[L2Network]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[L2Network]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                **kwargs: Any
            ) -> L2Network: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[L2Network]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[L2Network]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_update_parameters: Optional[L2NetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L2Network: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L2Network: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L2Network: ...


    class azure.mgmt.networkcloud.aio.operations.L3NetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_parameters: L3Network, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[L3Network]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[L3Network]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[L3Network]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                **kwargs: Any
            ) -> L3Network: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[L3Network]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[L3Network]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_update_parameters: Optional[L3NetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L3Network: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L3Network: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L3Network: ...


    class azure.mgmt.networkcloud.aio.operations.MetricsConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_parameters: ClusterMetricsConfiguration, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterMetricsConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterMetricsConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterMetricsConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_update_parameters: Optional[ClusterMetricsConfigurationPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterMetricsConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterMetricsConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterMetricsConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                **kwargs: Any
            ) -> ClusterMetricsConfiguration: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterMetricsConfiguration]: ...


    class azure.mgmt.networkcloud.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.networkcloud.aio.operations.RackSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                rack_sku_name: str, 
                **kwargs: Any
            ) -> RackSku: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[RackSku]: ...


    class azure.mgmt.networkcloud.aio.operations.RacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_parameters: Rack, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Rack]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Rack]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Rack]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_update_parameters: Optional[RackPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Rack]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Rack]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Rack]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                **kwargs: Any
            ) -> Rack: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Rack]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Rack]: ...


    class azure.mgmt.networkcloud.aio.operations.StorageAppliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_parameters: StorageAppliance, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAppliance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAppliance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAppliance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_disable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_enable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_enable_remote_vendor_management_parameters: Optional[StorageApplianceEnableRemoteVendorManagementParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_enable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_enable_remote_vendor_management_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_enable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_enable_remote_vendor_management_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_run_read_commands_parameters: StorageApplianceRunReadCommandsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_run_read_commands_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_run_read_commands_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_update_parameters: Optional[StorageAppliancePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAppliance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAppliance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAppliance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                **kwargs: Any
            ) -> StorageAppliance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageAppliance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageAppliance]: ...


    class azure.mgmt.networkcloud.aio.operations.TrunkedNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_parameters: TrunkedNetwork, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TrunkedNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TrunkedNetwork]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TrunkedNetwork]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                **kwargs: Any
            ) -> TrunkedNetwork: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TrunkedNetwork]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TrunkedNetwork]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_update_parameters: Optional[TrunkedNetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> TrunkedNetwork: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> TrunkedNetwork: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> TrunkedNetwork: ...


    class azure.mgmt.networkcloud.aio.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_assign_relay(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_assign_relay_parameters: Optional[VirtualMachineAssignRelayParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_assign_relay(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_assign_relay_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_assign_relay(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_assign_relay_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_parameters: VirtualMachine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_power_off_parameters: Optional[VirtualMachinePowerOffParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_power_off_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_power_off_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_update_parameters: Optional[VirtualMachinePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...


    class azure.mgmt.networkcloud.aio.operations.VolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_parameters: Volume, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Volume]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Volume]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_update_parameters: Optional[VolumePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Volume: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Volume: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Volume: ...


namespace azure.mgmt.networkcloud.models

    class azure.mgmt.networkcloud.models.AadConfiguration(_Model):
        admin_group_object_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_group_object_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ActionState(_Model):
        action_type: Optional[str]
        correlation_id: Optional[str]
        end_time: Optional[str]
        message: Optional[str]
        start_time: Optional[str]
        status: Optional[Union[str, ActionStateStatus]]
        step_states: Optional[list[StepState]]


    class azure.mgmt.networkcloud.models.ActionStateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.networkcloud.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.networkcloud.models.AdministrativeCredentials(_Model):
        password: str
        username: str

        @overload
        def __init__(
                self, 
                *, 
                password: str, 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AdministratorConfiguration(_Model):
        admin_username: Optional[str]
        ssh_public_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                admin_username: Optional[str] = ..., 
                ssh_public_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AdministratorConfigurationPatch(_Model):
        ssh_public_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                ssh_public_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AdvertiseToFabric(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.AgentOptions(_Model):
        hugepages_count: int
        hugepages_size: Optional[Union[str, HugepagesSize]]

        @overload
        def __init__(
                self, 
                *, 
                hugepages_count: int, 
                hugepages_size: Optional[Union[str, HugepagesSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AgentPool(TrackedResource):
        etag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: AgentPoolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: AgentPoolProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.AgentPoolDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.AgentPoolMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "NotApplicable"
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.networkcloud.models.AgentPoolPatchParameters(_Model):
        properties: Optional[AgentPoolPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgentPoolPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.AgentPoolPatchProperties(_Model):
        administrator_configuration: Optional[NodePoolAdministratorConfigurationPatch]
        count: Optional[int]
        upgrade_settings: Optional[AgentPoolUpgradeSettings]

        @overload
        def __init__(
                self, 
                *, 
                administrator_configuration: Optional[NodePoolAdministratorConfigurationPatch] = ..., 
                count: Optional[int] = ..., 
                upgrade_settings: Optional[AgentPoolUpgradeSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AgentPoolProperties(_Model):
        administrator_configuration: Optional[AdministratorConfiguration]
        agent_options: Optional[AgentOptions]
        attached_network_configuration: Optional[AttachedNetworkConfiguration]
        availability_zones: Optional[list[str]]
        count: int
        detailed_status: Optional[Union[str, AgentPoolDetailedStatus]]
        detailed_status_message: Optional[str]
        kubernetes_version: Optional[str]
        labels: Optional[list[KubernetesLabel]]
        mode: Union[str, AgentPoolMode]
        provisioning_state: Optional[Union[str, AgentPoolProvisioningState]]
        taints: Optional[list[KubernetesLabel]]
        upgrade_settings: Optional[AgentPoolUpgradeSettings]
        vm_sku_name: str

        @overload
        def __init__(
                self, 
                *, 
                administrator_configuration: Optional[AdministratorConfiguration] = ..., 
                agent_options: Optional[AgentOptions] = ..., 
                attached_network_configuration: Optional[AttachedNetworkConfiguration] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                count: int, 
                labels: Optional[list[KubernetesLabel]] = ..., 
                mode: Union[str, AgentPoolMode], 
                taints: Optional[list[KubernetesLabel]] = ..., 
                upgrade_settings: Optional[AgentPoolUpgradeSettings] = ..., 
                vm_sku_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AgentPoolProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networkcloud.models.AgentPoolUpgradeSettings(_Model):
        drain_timeout: Optional[int]
        max_surge: Optional[str]
        max_unavailable: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                drain_timeout: Optional[int] = ..., 
                max_surge: Optional[str] = ..., 
                max_unavailable: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AnalyticsOutputSettings(_Model):
        analytics_workspace_id: Optional[str]
        associated_identity: Optional[IdentitySelector]

        @overload
        def __init__(
                self, 
                *, 
                analytics_workspace_id: Optional[str] = ..., 
                associated_identity: Optional[IdentitySelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AttachedNetworkConfiguration(_Model):
        l2_networks: Optional[list[L2NetworkAttachmentConfiguration]]
        l3_networks: Optional[list[L3NetworkAttachmentConfiguration]]
        trunked_networks: Optional[list[TrunkedNetworkAttachmentConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                l2_networks: Optional[list[L2NetworkAttachmentConfiguration]] = ..., 
                l3_networks: Optional[list[L3NetworkAttachmentConfiguration]] = ..., 
                trunked_networks: Optional[list[TrunkedNetworkAttachmentConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.AvailabilityLifecycle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERALLY_AVAILABLE = "GenerallyAvailable"
        PREVIEW = "Preview"


    class azure.mgmt.networkcloud.models.AvailableUpgrade(_Model):
        availability_lifecycle: Optional[Union[str, AvailabilityLifecycle]]
        version: Optional[str]


    class azure.mgmt.networkcloud.models.BareMetalMachine(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: BareMetalMachineProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: BareMetalMachineProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineCommandSpecification(_Model):
        arguments: Optional[list[str]]
        command: str

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[list[str]] = ..., 
                command: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineConfigurationData(_Model):
        bmc_connection_string: Optional[str]
        bmc_credentials: AdministrativeCredentials
        bmc_mac_address: str
        boot_mac_address: str
        machine_details: Optional[str]
        machine_name: Optional[str]
        rack_slot: int
        serial_number: str

        @overload
        def __init__(
                self, 
                *, 
                bmc_credentials: AdministrativeCredentials, 
                bmc_mac_address: str, 
                boot_mac_address: str, 
                machine_details: Optional[str] = ..., 
                machine_name: Optional[str] = ..., 
                rack_slot: int, 
                serial_number: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineCordonParameters(_Model):
        evacuate: Optional[Union[str, BareMetalMachineEvacuate]]

        @overload
        def __init__(
                self, 
                *, 
                evacuate: Optional[Union[str, BareMetalMachineEvacuate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineCordonStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CORDONED = "Cordoned"
        UNCORDONED = "Uncordoned"


    class azure.mgmt.networkcloud.models.BareMetalMachineDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEPROVISIONING = "Deprovisioning"
        ERROR = "Error"
        PREPARING = "Preparing"
        PROVISIONED = "Provisioned"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.BareMetalMachineEvacuate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.BareMetalMachineHardwareValidationResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL = "Fail"
        PASS = "Pass"


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySet(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: BareMetalMachineKeySetProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: BareMetalMachineKeySetProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySetDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_ACTIVE = "AllActive"
        ALL_INVALID = "AllInvalid"
        SOME_INVALID = "SomeInvalid"
        VALIDATING = "Validating"


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySetPatchParameters(_Model):
        properties: Optional[BareMetalMachineKeySetPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BareMetalMachineKeySetPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySetPatchProperties(_Model):
        expiration: Optional[datetime]
        jump_hosts_allowed: Optional[list[str]]
        user_list: Optional[list[KeySetUser]]

        @overload
        def __init__(
                self, 
                *, 
                expiration: Optional[datetime] = ..., 
                jump_hosts_allowed: Optional[list[str]] = ..., 
                user_list: Optional[list[KeySetUser]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySetPrivilegeLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "Other"
        STANDARD = "Standard"
        SUPERUSER = "Superuser"


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySetProperties(_Model):
        azure_group_id: str
        detailed_status: Optional[Union[str, BareMetalMachineKeySetDetailedStatus]]
        detailed_status_message: Optional[str]
        expiration: datetime
        jump_hosts_allowed: list[str]
        last_validation: Optional[datetime]
        os_group_name: Optional[str]
        privilege_level: Union[str, BareMetalMachineKeySetPrivilegeLevel]
        privilege_level_name: Optional[str]
        provisioning_state: Optional[Union[str, BareMetalMachineKeySetProvisioningState]]
        user_list: list[KeySetUser]
        user_list_status: Optional[list[KeySetUserStatus]]

        @overload
        def __init__(
                self, 
                *, 
                azure_group_id: str, 
                expiration: datetime, 
                jump_hosts_allowed: list[str], 
                os_group_name: Optional[str] = ..., 
                privilege_level: Union[str, BareMetalMachineKeySetPrivilegeLevel], 
                privilege_level_name: Optional[str] = ..., 
                user_list: list[KeySetUser]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySetProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.BareMetalMachineKeySetUserSetupStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INVALID = "Invalid"


    class azure.mgmt.networkcloud.models.BareMetalMachinePatchParameters(_Model):
        properties: Optional[BareMetalMachinePatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BareMetalMachinePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachinePatchProperties(_Model):
        machine_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                machine_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachinePowerOffParameters(_Model):
        skip_shutdown: Optional[Union[str, BareMetalMachineSkipShutdown]]

        @overload
        def __init__(
                self, 
                *, 
                skip_shutdown: Optional[Union[str, BareMetalMachineSkipShutdown]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachinePowerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"


    class azure.mgmt.networkcloud.models.BareMetalMachineProperties(_Model):
        action_states: Optional[list[ActionState]]
        associated_resource_ids: Optional[list[str]]
        bmc_connection_string: str
        bmc_credentials: AdministrativeCredentials
        bmc_mac_address: str
        boot_mac_address: str
        ca_certificate: Optional[CertificateInfo]
        cluster_id: Optional[str]
        cordon_status: Optional[Union[str, BareMetalMachineCordonStatus]]
        detailed_status: Optional[Union[str, BareMetalMachineDetailedStatus]]
        detailed_status_message: Optional[str]
        hardware_inventory: Optional[HardwareInventory]
        hardware_validation_status: Optional[HardwareValidationStatus]
        hybrid_aks_clusters_associated_ids: Optional[list[str]]
        kubernetes_node_name: Optional[str]
        kubernetes_version: Optional[str]
        machine_cluster_version: Optional[str]
        machine_details: str
        machine_name: str
        machine_roles: Optional[list[str]]
        machine_sku_id: str
        oam_ipv4_address: Optional[str]
        oam_ipv6_address: Optional[str]
        os_image: Optional[str]
        power_state: Optional[Union[str, BareMetalMachinePowerState]]
        provisioning_state: Optional[Union[str, BareMetalMachineProvisioningState]]
        rack_id: str
        rack_slot: int
        ready_state: Optional[Union[str, BareMetalMachineReadyState]]
        runtime_protection_status: Optional[RuntimeProtectionStatus]
        secret_rotation_status: Optional[list[SecretRotationStatus]]
        serial_number: str
        service_tag: Optional[str]
        virtual_machines_associated_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                bmc_connection_string: str, 
                bmc_credentials: AdministrativeCredentials, 
                bmc_mac_address: str, 
                boot_mac_address: str, 
                machine_cluster_version: Optional[str] = ..., 
                machine_details: str, 
                machine_name: str, 
                machine_sku_id: str, 
                rack_id: str, 
                rack_slot: int, 
                serial_number: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.BareMetalMachineReadyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.BareMetalMachineReplaceParameters(_Model):
        bmc_credentials: Optional[AdministrativeCredentials]
        bmc_mac_address: Optional[str]
        boot_mac_address: Optional[str]
        machine_name: Optional[str]
        safeguard_mode: Optional[Union[str, BareMetalMachineReplaceSafeguardMode]]
        serial_number: Optional[str]
        storage_policy: Optional[Union[str, BareMetalMachineReplaceStoragePolicy]]

        @overload
        def __init__(
                self, 
                *, 
                bmc_credentials: Optional[AdministrativeCredentials] = ..., 
                bmc_mac_address: Optional[str] = ..., 
                boot_mac_address: Optional[str] = ..., 
                machine_name: Optional[str] = ..., 
                safeguard_mode: Optional[Union[str, BareMetalMachineReplaceSafeguardMode]] = ..., 
                serial_number: Optional[str] = ..., 
                storage_policy: Optional[Union[str, BareMetalMachineReplaceStoragePolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineReplaceSafeguardMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        NONE = "None"


    class azure.mgmt.networkcloud.models.BareMetalMachineReplaceStoragePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISCARD_ALL = "DiscardAll"
        PRESERVE = "Preserve"


    class azure.mgmt.networkcloud.models.BareMetalMachineRunCommandParameters(_Model):
        arguments: Optional[list[str]]
        limit_time_seconds: int
        script: str

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[list[str]] = ..., 
                limit_time_seconds: int, 
                script: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineRunDataExtractsParameters(_Model):
        commands: list[BareMetalMachineCommandSpecification]
        limit_time_seconds: int

        @overload
        def __init__(
                self, 
                *, 
                commands: list[BareMetalMachineCommandSpecification], 
                limit_time_seconds: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineRunReadCommandsParameters(_Model):
        commands: list[BareMetalMachineCommandSpecification]
        limit_time_seconds: int

        @overload
        def __init__(
                self, 
                *, 
                commands: list[BareMetalMachineCommandSpecification], 
                limit_time_seconds: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BareMetalMachineSkipShutdown(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.BfdEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.BgpAdvertisement(_Model):
        advertise_to_fabric: Optional[Union[str, AdvertiseToFabric]]
        communities: Optional[list[str]]
        ip_address_pools: list[str]
        peers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                advertise_to_fabric: Optional[Union[str, AdvertiseToFabric]] = ..., 
                communities: Optional[list[str]] = ..., 
                ip_address_pools: list[str], 
                peers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BgpMultiHop(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.BgpServiceLoadBalancerConfiguration(_Model):
        bgp_advertisements: Optional[list[BgpAdvertisement]]
        bgp_peers: Optional[list[ServiceLoadBalancerBgpPeer]]
        fabric_peering_enabled: Optional[Union[str, FabricPeeringEnabled]]
        ip_address_pools: Optional[list[IpAddressPool]]

        @overload
        def __init__(
                self, 
                *, 
                bgp_advertisements: Optional[list[BgpAdvertisement]] = ..., 
                bgp_peers: Optional[list[ServiceLoadBalancerBgpPeer]] = ..., 
                fabric_peering_enabled: Optional[Union[str, FabricPeeringEnabled]] = ..., 
                ip_address_pools: Optional[list[IpAddressPool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BmcKeySet(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: BmcKeySetProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: BmcKeySetProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.BmcKeySetDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_ACTIVE = "AllActive"
        ALL_INVALID = "AllInvalid"
        SOME_INVALID = "SomeInvalid"
        VALIDATING = "Validating"


    class azure.mgmt.networkcloud.models.BmcKeySetPatchParameters(_Model):
        properties: Optional[BmcKeySetPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BmcKeySetPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.BmcKeySetPatchProperties(_Model):
        expiration: Optional[datetime]
        user_list: Optional[list[KeySetUser]]

        @overload
        def __init__(
                self, 
                *, 
                expiration: Optional[datetime] = ..., 
                user_list: Optional[list[KeySetUser]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BmcKeySetPrivilegeLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMINISTRATOR = "Administrator"
        READ_ONLY = "ReadOnly"


    class azure.mgmt.networkcloud.models.BmcKeySetProperties(_Model):
        azure_group_id: str
        detailed_status: Optional[Union[str, BmcKeySetDetailedStatus]]
        detailed_status_message: Optional[str]
        expiration: datetime
        last_validation: Optional[datetime]
        privilege_level: Union[str, BmcKeySetPrivilegeLevel]
        provisioning_state: Optional[Union[str, BmcKeySetProvisioningState]]
        user_list: list[KeySetUser]
        user_list_status: Optional[list[KeySetUserStatus]]

        @overload
        def __init__(
                self, 
                *, 
                azure_group_id: str, 
                expiration: datetime, 
                privilege_level: Union[str, BmcKeySetPrivilegeLevel], 
                user_list: list[KeySetUser]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.BmcKeySetProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.BootstrapProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PXE = "PXE"


    class azure.mgmt.networkcloud.models.CertificateInfo(_Model):
        hash: Optional[str]
        value: Optional[str]


    class azure.mgmt.networkcloud.models.CloudServicesNetwork(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[CloudServicesNetworkProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[CloudServicesNetworkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.CloudServicesNetworkDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.CloudServicesNetworkEnableDefaultEgressEndpoints(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.CloudServicesNetworkPatchParameters(_Model):
        properties: Optional[CloudServicesNetworkPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudServicesNetworkPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.CloudServicesNetworkPatchProperties(_Model):
        additional_egress_endpoints: Optional[list[EgressEndpoint]]
        enable_default_egress_endpoints: Optional[Union[str, CloudServicesNetworkEnableDefaultEgressEndpoints]]
        storage_options: Optional[CloudServicesNetworkStorageOptionsPatch]

        @overload
        def __init__(
                self, 
                *, 
                additional_egress_endpoints: Optional[list[EgressEndpoint]] = ..., 
                enable_default_egress_endpoints: Optional[Union[str, CloudServicesNetworkEnableDefaultEgressEndpoints]] = ..., 
                storage_options: Optional[CloudServicesNetworkStorageOptionsPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CloudServicesNetworkProperties(_Model):
        additional_egress_endpoints: Optional[list[EgressEndpoint]]
        associated_resource_ids: Optional[list[str]]
        cluster_id: Optional[str]
        detailed_status: Optional[Union[str, CloudServicesNetworkDetailedStatus]]
        detailed_status_message: Optional[str]
        enable_default_egress_endpoints: Optional[Union[str, CloudServicesNetworkEnableDefaultEgressEndpoints]]
        enabled_egress_endpoints: Optional[list[EgressEndpoint]]
        hybrid_aks_clusters_associated_ids: Optional[list[str]]
        interface_name: Optional[str]
        provisioning_state: Optional[Union[str, CloudServicesNetworkProvisioningState]]
        storage_options: Optional[CloudServicesNetworkStorageOptions]
        storage_status: Optional[CloudServicesNetworkStorageStatus]
        virtual_machines_associated_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                additional_egress_endpoints: Optional[list[EgressEndpoint]] = ..., 
                enable_default_egress_endpoints: Optional[Union[str, CloudServicesNetworkEnableDefaultEgressEndpoints]] = ..., 
                storage_options: Optional[CloudServicesNetworkStorageOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CloudServicesNetworkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.CloudServicesNetworkStorageMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        STANDARD = "Standard"


    class azure.mgmt.networkcloud.models.CloudServicesNetworkStorageOptions(_Model):
        mode: Optional[Union[str, CloudServicesNetworkStorageMode]]
        size_mi_b: Optional[int]
        storage_appliance_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, CloudServicesNetworkStorageMode]] = ..., 
                size_mi_b: Optional[int] = ..., 
                storage_appliance_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CloudServicesNetworkStorageOptionsPatch(_Model):
        mode: Optional[Union[str, CloudServicesNetworkStorageMode]]
        size_mi_b: Optional[int]
        storage_appliance_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, CloudServicesNetworkStorageMode]] = ..., 
                size_mi_b: Optional[int] = ..., 
                storage_appliance_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CloudServicesNetworkStorageStatus(_Model):
        mode: Optional[Union[str, CloudServicesNetworkStorageMode]]
        size_mi_b: Optional[int]
        status: Optional[Union[str, CloudServicesNetworkStorageStatusStatus]]
        status_message: Optional[str]
        volume_id: Optional[str]


    class azure.mgmt.networkcloud.models.CloudServicesNetworkStorageStatusStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        EXPANDING_VOLUME = "ExpandingVolume"
        EXPANSION_FAILED = "ExpansionFailed"


    class azure.mgmt.networkcloud.models.Cluster(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: ClusterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: ClusterProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterAvailableUpgradeVersion(_Model):
        control_impact: Optional[Union[str, ControlImpact]]
        expected_duration: Optional[str]
        impact_description: Optional[str]
        support_expiry_date: Optional[str]
        target_cluster_version: Optional[str]
        workload_impact: Optional[Union[str, WorkloadImpact]]


    class azure.mgmt.networkcloud.models.ClusterAvailableVersion(_Model):
        support_expiry_date: Optional[str]
        target_cluster_version: Optional[str]


    class azure.mgmt.networkcloud.models.ClusterCapacity(_Model):
        available_appliance_storage_gb: Optional[int]
        available_core_count: Optional[int]
        available_host_storage_gb: Optional[int]
        available_memory_gb: Optional[int]
        total_appliance_storage_gb: Optional[int]
        total_core_count: Optional[int]
        total_host_storage_gb: Optional[int]
        total_memory_gb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                available_appliance_storage_gb: Optional[int] = ..., 
                available_core_count: Optional[int] = ..., 
                available_host_storage_gb: Optional[int] = ..., 
                available_memory_gb: Optional[int] = ..., 
                total_appliance_storage_gb: Optional[int] = ..., 
                total_core_count: Optional[int] = ..., 
                total_host_storage_gb: Optional[int] = ..., 
                total_memory_gb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        TIMEOUT = "Timeout"
        UNDEFINED = "Undefined"


    class azure.mgmt.networkcloud.models.ClusterContinueUpdateVersionMachineGroupTargetingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALPHA_BY_RACK = "AlphaByRack"


    class azure.mgmt.networkcloud.models.ClusterContinueUpdateVersionParameters(_Model):
        machine_group_targeting_mode: Optional[Union[str, ClusterContinueUpdateVersionMachineGroupTargetingMode]]

        @overload
        def __init__(
                self, 
                *, 
                machine_group_targeting_mode: Optional[Union[str, ClusterContinueUpdateVersionMachineGroupTargetingMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterDeployParameters(_Model):
        skip_validations_for_machines: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                skip_validations_for_machines: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        DELETING = "Deleting"
        DEPLOYING = "Deploying"
        DISCONNECTED = "Disconnected"
        FAILED = "Failed"
        PENDING_DEPLOYMENT = "PendingDeployment"
        RUNNING = "Running"
        UPDATE_PAUSED = "UpdatePaused"
        UPDATING = "Updating"


    class azure.mgmt.networkcloud.models.ClusterManager(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: ClusterManagerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: ClusterManagerProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterManagerConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        UNREACHABLE = "Unreachable"


    class azure.mgmt.networkcloud.models.ClusterManagerDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"
        PROVISIONING_FAILED = "ProvisioningFailed"
        UPDATE_FAILED = "UpdateFailed"
        UPDATING = "Updating"


    class azure.mgmt.networkcloud.models.ClusterManagerPatchParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterManagerProperties(_Model):
        analytics_workspace_id: Optional[str]
        availability_zones: Optional[list[str]]
        cluster_versions: Optional[list[ClusterAvailableVersion]]
        detailed_status: Optional[Union[str, ClusterManagerDetailedStatus]]
        detailed_status_message: Optional[str]
        fabric_controller_id: str
        managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration]
        manager_extended_location: Optional[ExtendedLocation]
        provisioning_state: Optional[Union[str, ClusterManagerProvisioningState]]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                analytics_workspace_id: Optional[str] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                fabric_controller_id: str, 
                managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterManagerProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networkcloud.models.ClusterMetricsConfiguration(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: ClusterMetricsConfigurationProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: ClusterMetricsConfigurationProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterMetricsConfigurationDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLIED = "Applied"
        ERROR = "Error"
        PROCESSING = "Processing"


    class azure.mgmt.networkcloud.models.ClusterMetricsConfigurationPatchParameters(_Model):
        properties: Optional[ClusterMetricsConfigurationPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterMetricsConfigurationPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterMetricsConfigurationPatchProperties(_Model):
        collection_interval: Optional[int]
        enabled_metrics: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                collection_interval: Optional[int] = ..., 
                enabled_metrics: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterMetricsConfigurationProperties(_Model):
        collection_interval: int
        detailed_status: Optional[Union[str, ClusterMetricsConfigurationDetailedStatus]]
        detailed_status_message: Optional[str]
        disabled_metrics: Optional[list[str]]
        enabled_metrics: Optional[list[str]]
        provisioning_state: Optional[Union[str, ClusterMetricsConfigurationProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                collection_interval: int, 
                enabled_metrics: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterMetricsConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.ClusterPatchParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ClusterPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ClusterPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterPatchProperties(_Model):
        aggregator_or_single_rack_definition: Optional[RackDefinition]
        analytics_output_settings: Optional[AnalyticsOutputSettings]
        cluster_location: Optional[str]
        cluster_service_principal: Optional[ServicePrincipalInformation]
        command_output_settings: Optional[CommandOutputSettings]
        compute_deployment_threshold: Optional[ValidationThreshold]
        compute_rack_definitions: Optional[list[RackDefinition]]
        runtime_protection_configuration: Optional[RuntimeProtectionConfiguration]
        secret_archive: Optional[ClusterSecretArchive]
        secret_archive_settings: Optional[SecretArchiveSettings]
        update_strategy: Optional[ClusterUpdateStrategy]
        vulnerability_scanning_settings: Optional[VulnerabilityScanningSettingsPatch]

        @overload
        def __init__(
                self, 
                *, 
                aggregator_or_single_rack_definition: Optional[RackDefinition] = ..., 
                analytics_output_settings: Optional[AnalyticsOutputSettings] = ..., 
                cluster_location: Optional[str] = ..., 
                cluster_service_principal: Optional[ServicePrincipalInformation] = ..., 
                command_output_settings: Optional[CommandOutputSettings] = ..., 
                compute_deployment_threshold: Optional[ValidationThreshold] = ..., 
                compute_rack_definitions: Optional[list[RackDefinition]] = ..., 
                runtime_protection_configuration: Optional[RuntimeProtectionConfiguration] = ..., 
                secret_archive: Optional[ClusterSecretArchive] = ..., 
                secret_archive_settings: Optional[SecretArchiveSettings] = ..., 
                update_strategy: Optional[ClusterUpdateStrategy] = ..., 
                vulnerability_scanning_settings: Optional[VulnerabilityScanningSettingsPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterProperties(_Model):
        action_states: Optional[list[ActionState]]
        aggregator_or_single_rack_definition: RackDefinition
        analytics_output_settings: Optional[AnalyticsOutputSettings]
        analytics_workspace_id: Optional[str]
        available_upgrade_versions: Optional[list[ClusterAvailableUpgradeVersion]]
        cluster_capacity: Optional[ClusterCapacity]
        cluster_connection_status: Optional[Union[str, ClusterConnectionStatus]]
        cluster_extended_location: Optional[ExtendedLocation]
        cluster_location: Optional[str]
        cluster_manager_connection_status: Optional[Union[str, ClusterManagerConnectionStatus]]
        cluster_manager_id: Optional[str]
        cluster_service_principal: Optional[ServicePrincipalInformation]
        cluster_type: Union[str, ClusterType]
        cluster_version: str
        command_output_settings: Optional[CommandOutputSettings]
        compute_deployment_threshold: Optional[ValidationThreshold]
        compute_rack_definitions: Optional[list[RackDefinition]]
        detailed_status: Optional[Union[str, ClusterDetailedStatus]]
        detailed_status_message: Optional[str]
        hybrid_aks_extended_location: Optional[ExtendedLocation]
        managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration]
        manual_action_count: Optional[int]
        network_fabric_id: str
        provisioning_state: Optional[Union[str, ClusterProvisioningState]]
        runtime_protection_configuration: Optional[RuntimeProtectionConfiguration]
        secret_archive: Optional[ClusterSecretArchive]
        secret_archive_settings: Optional[SecretArchiveSettings]
        support_expiry_date: Optional[str]
        update_strategy: Optional[ClusterUpdateStrategy]
        vulnerability_scanning_settings: Optional[VulnerabilityScanningSettings]
        workload_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                aggregator_or_single_rack_definition: RackDefinition, 
                analytics_output_settings: Optional[AnalyticsOutputSettings] = ..., 
                analytics_workspace_id: Optional[str] = ..., 
                cluster_location: Optional[str] = ..., 
                cluster_service_principal: Optional[ServicePrincipalInformation] = ..., 
                cluster_type: Union[str, ClusterType], 
                cluster_version: str, 
                command_output_settings: Optional[CommandOutputSettings] = ..., 
                compute_deployment_threshold: Optional[ValidationThreshold] = ..., 
                compute_rack_definitions: Optional[list[RackDefinition]] = ..., 
                managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration] = ..., 
                network_fabric_id: str, 
                runtime_protection_configuration: Optional[RuntimeProtectionConfiguration] = ..., 
                secret_archive: Optional[ClusterSecretArchive] = ..., 
                secret_archive_settings: Optional[SecretArchiveSettings] = ..., 
                update_strategy: Optional[ClusterUpdateStrategy] = ..., 
                vulnerability_scanning_settings: Optional[VulnerabilityScanningSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"
        VALIDATING = "Validating"


    class azure.mgmt.networkcloud.models.ClusterScanRuntimeParameters(_Model):
        scan_activity: Optional[Union[str, ClusterScanRuntimeParametersScanActivity]]

        @overload
        def __init__(
                self, 
                *, 
                scan_activity: Optional[Union[str, ClusterScanRuntimeParametersScanActivity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterScanRuntimeParametersScanActivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCAN = "Scan"
        SKIP = "Skip"


    class azure.mgmt.networkcloud.models.ClusterSecretArchive(_Model):
        key_vault_id: str
        use_key_vault: Optional[Union[str, ClusterSecretArchiveEnabled]]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_id: str, 
                use_key_vault: Optional[Union[str, ClusterSecretArchiveEnabled]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterSecretArchiveEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.ClusterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_RACK = "MultiRack"
        SINGLE_RACK = "SingleRack"


    class azure.mgmt.networkcloud.models.ClusterUpdateStrategy(_Model):
        max_unavailable: Optional[int]
        strategy_type: Union[str, ClusterUpdateStrategyType]
        threshold_type: Union[str, ValidationThresholdType]
        threshold_value: int
        wait_time_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_unavailable: Optional[int] = ..., 
                strategy_type: Union[str, ClusterUpdateStrategyType], 
                threshold_type: Union[str, ValidationThresholdType], 
                threshold_value: int, 
                wait_time_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ClusterUpdateStrategyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAUSE_AFTER_RACK = "PauseAfterRack"
        RACK = "Rack"


    class azure.mgmt.networkcloud.models.ClusterUpdateVersionParameters(_Model):
        target_cluster_version: str

        @overload
        def __init__(
                self, 
                *, 
                target_cluster_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CommandOutputOverride(_Model):
        associated_identity: Optional[IdentitySelector]
        command_output_type: Optional[Union[str, CommandOutputType]]
        container_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                associated_identity: Optional[IdentitySelector] = ..., 
                command_output_type: Optional[Union[str, CommandOutputType]] = ..., 
                container_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CommandOutputSettings(_Model):
        associated_identity: Optional[IdentitySelector]
        container_url: Optional[str]
        overrides: Optional[list[CommandOutputOverride]]

        @overload
        def __init__(
                self, 
                *, 
                associated_identity: Optional[IdentitySelector] = ..., 
                container_url: Optional[str] = ..., 
                overrides: Optional[list[CommandOutputOverride]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CommandOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BARE_METAL_MACHINE_RUN_COMMAND = "BareMetalMachineRunCommand"
        BARE_METAL_MACHINE_RUN_DATA_EXTRACTS = "BareMetalMachineRunDataExtracts"
        BARE_METAL_MACHINE_RUN_DATA_EXTRACTS_RESTRICTED = "BareMetalMachineRunDataExtractsRestricted"
        BARE_METAL_MACHINE_RUN_READ_COMMANDS = "BareMetalMachineRunReadCommands"
        STORAGE_RUN_READ_COMMANDS = "StorageRunReadCommands"


    class azure.mgmt.networkcloud.models.Console(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: ConsoleProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: ConsoleProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ConsoleDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        READY = "Ready"


    class azure.mgmt.networkcloud.models.ConsoleEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.ConsolePatchParameters(_Model):
        properties: Optional[ConsolePatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConsolePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ConsolePatchProperties(_Model):
        enabled: Optional[Union[str, ConsoleEnabled]]
        expiration: Optional[datetime]
        ssh_public_key: Optional[SshPublicKey]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[Union[str, ConsoleEnabled]] = ..., 
                expiration: Optional[datetime] = ..., 
                ssh_public_key: Optional[SshPublicKey] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ConsoleProperties(_Model):
        detailed_status: Optional[Union[str, ConsoleDetailedStatus]]
        detailed_status_message: Optional[str]
        enabled: Union[str, ConsoleEnabled]
        expiration: Optional[datetime]
        private_link_service_id: Optional[str]
        provisioning_state: Optional[Union[str, ConsoleProvisioningState]]
        ssh_public_key: SshPublicKey
        virtual_machine_access_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Union[str, ConsoleEnabled], 
                expiration: Optional[datetime] = ..., 
                ssh_public_key: SshPublicKey
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ConsoleProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.ControlImpact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.ControlPlaneNodeConfiguration(_Model):
        administrator_configuration: Optional[AdministratorConfiguration]
        availability_zones: Optional[list[str]]
        count: int
        vm_sku_name: str

        @overload
        def __init__(
                self, 
                *, 
                administrator_configuration: Optional[AdministratorConfiguration] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                count: int, 
                vm_sku_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ControlPlaneNodePatchConfiguration(_Model):
        administrator_configuration: Optional[AdministratorConfigurationPatch]
        count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                administrator_configuration: Optional[AdministratorConfigurationPatch] = ..., 
                count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.networkcloud.models.DefaultGateway(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.DeviceConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCI = "PCI"


    class azure.mgmt.networkcloud.models.DiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HDD = "HDD"
        SSD = "SSD"


    class azure.mgmt.networkcloud.models.EgressEndpoint(_Model):
        category: str
        endpoints: list[EndpointDependency]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                endpoints: list[EndpointDependency]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.EndpointDependency(_Model):
        domain_name: str
        port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: str, 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.networkcloud.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.networkcloud.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ExtendedLocation(_Model):
        name: str
        type: Union[str, ExtendedLocationType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, ExtendedLocationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.networkcloud.models.FabricPeeringEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.FeatureDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        RUNNING = "Running"
        UNKNOWN = "Unknown"


    class azure.mgmt.networkcloud.models.FeatureStatus(_Model):
        detailed_status: Optional[Union[str, FeatureDetailedStatus]]
        detailed_status_message: Optional[str]
        name: Optional[str]
        version: Optional[str]


    class azure.mgmt.networkcloud.models.HardwareInventory(_Model):
        additional_host_information: Optional[str]
        interfaces: Optional[list[HardwareInventoryNetworkInterface]]
        nics: Optional[list[Nic]]


    class azure.mgmt.networkcloud.models.HardwareInventoryNetworkInterface(_Model):
        link_status: Optional[str]
        mac_address: Optional[str]
        name: Optional[str]
        network_interface_id: Optional[str]


    class azure.mgmt.networkcloud.models.HardwareValidationStatus(_Model):
        last_validation_time: Optional[datetime]
        result: Optional[Union[str, BareMetalMachineHardwareValidationResult]]


    class azure.mgmt.networkcloud.models.HugepagesSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE_G = "1G"
        TWO_M = "2M"


    class azure.mgmt.networkcloud.models.HybridAksIpamEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.HybridAksPluginType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DPDK = "DPDK"
        OS_DEVICE = "OSDevice"
        SRIOV = "SRIOV"


    class azure.mgmt.networkcloud.models.IdentitySelector(_Model):
        identity_type: Optional[Union[str, ManagedServiceIdentitySelectorType]]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_type: Optional[Union[str, ManagedServiceIdentitySelectorType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ImageRepositoryCredentials(_Model):
        password: str
        registry_url: str
        username: str

        @overload
        def __init__(
                self, 
                *, 
                password: str, 
                registry_url: str, 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.InitialAgentPoolConfiguration(_Model):
        administrator_configuration: Optional[AdministratorConfiguration]
        agent_options: Optional[AgentOptions]
        attached_network_configuration: Optional[AttachedNetworkConfiguration]
        availability_zones: Optional[list[str]]
        count: int
        labels: Optional[list[KubernetesLabel]]
        mode: Union[str, AgentPoolMode]
        name: str
        taints: Optional[list[KubernetesLabel]]
        upgrade_settings: Optional[AgentPoolUpgradeSettings]
        vm_sku_name: str

        @overload
        def __init__(
                self, 
                *, 
                administrator_configuration: Optional[AdministratorConfiguration] = ..., 
                agent_options: Optional[AgentOptions] = ..., 
                attached_network_configuration: Optional[AttachedNetworkConfiguration] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                count: int, 
                labels: Optional[list[KubernetesLabel]] = ..., 
                mode: Union[str, AgentPoolMode], 
                name: str, 
                taints: Optional[list[KubernetesLabel]] = ..., 
                upgrade_settings: Optional[AgentPoolUpgradeSettings] = ..., 
                vm_sku_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.IpAddressPool(_Model):
        addresses: list[str]
        auto_assign: Optional[Union[str, BfdEnabled]]
        name: str
        only_use_host_ips: Optional[Union[str, BfdEnabled]]

        @overload
        def __init__(
                self, 
                *, 
                addresses: list[str], 
                auto_assign: Optional[Union[str, BfdEnabled]] = ..., 
                name: str, 
                only_use_host_ips: Optional[Union[str, BfdEnabled]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.IpAllocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUAL_STACK = "DualStack"
        IPV4 = "IPV4"
        IPV6 = "IPV6"


    class azure.mgmt.networkcloud.models.KeySetUser(_Model):
        azure_user_name: str
        description: Optional[str]
        ssh_public_key: SshPublicKey
        user_principal_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_user_name: str, 
                description: Optional[str] = ..., 
                ssh_public_key: SshPublicKey, 
                user_principal_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.KeySetUserStatus(_Model):
        azure_user_name: Optional[str]
        status: Optional[Union[str, BareMetalMachineKeySetUserSetupStatus]]
        status_message: Optional[str]


    class azure.mgmt.networkcloud.models.KubernetesCluster(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: KubernetesClusterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: KubernetesClusterProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.KubernetesClusterFeature(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[KubernetesClusterFeatureProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[KubernetesClusterFeatureProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterFeatureAvailabilityLifecycle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERALLY_AVAILABLE = "GenerallyAvailable"
        PREVIEW = "Preview"


    class azure.mgmt.networkcloud.models.KubernetesClusterFeatureDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INSTALLED = "Installed"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.KubernetesClusterFeaturePatchParameters(_Model):
        properties: Optional[KubernetesClusterFeaturePatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[KubernetesClusterFeaturePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterFeaturePatchProperties(_Model):
        options: Optional[list[StringKeyValuePair]]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[list[StringKeyValuePair]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterFeatureProperties(_Model):
        availability_lifecycle: Optional[Union[str, KubernetesClusterFeatureAvailabilityLifecycle]]
        detailed_status: Optional[Union[str, KubernetesClusterFeatureDetailedStatus]]
        detailed_status_message: Optional[str]
        options: Optional[list[StringKeyValuePair]]
        provisioning_state: Optional[Union[str, KubernetesClusterFeatureProvisioningState]]
        required: Optional[Union[str, KubernetesClusterFeatureRequired]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                options: Optional[list[StringKeyValuePair]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterFeatureProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networkcloud.models.KubernetesClusterFeatureRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.KubernetesClusterNode(_Model):
        agent_pool_id: Optional[str]
        availability_zone: Optional[str]
        bare_metal_machine_id: Optional[str]
        cpu_cores: Optional[int]
        detailed_status: Optional[Union[str, KubernetesClusterNodeDetailedStatus]]
        detailed_status_message: Optional[str]
        disk_size_gb: Optional[int]
        image: Optional[str]
        kubernetes_version: Optional[str]
        labels: Optional[list[KubernetesLabel]]
        memory_size_gb: Optional[int]
        mode: Optional[Union[str, AgentPoolMode]]
        name: Optional[str]
        network_attachments: Optional[list[NetworkAttachment]]
        power_state: Optional[Union[str, KubernetesNodePowerState]]
        role: Optional[Union[str, KubernetesNodeRole]]
        taints: Optional[list[KubernetesLabel]]
        vm_sku_name: Optional[str]


    class azure.mgmt.networkcloud.models.KubernetesClusterNodeDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"
        RUNNING = "Running"
        SCHEDULING = "Scheduling"
        STOPPED = "Stopped"
        TERMINATING = "Terminating"
        UNKNOWN = "Unknown"


    class azure.mgmt.networkcloud.models.KubernetesClusterPatchParameters(_Model):
        properties: Optional[KubernetesClusterPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[KubernetesClusterPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterPatchProperties(_Model):
        administrator_configuration: Optional[AdministratorConfigurationPatch]
        control_plane_node_configuration: Optional[ControlPlaneNodePatchConfiguration]
        kubernetes_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrator_configuration: Optional[AdministratorConfigurationPatch] = ..., 
                control_plane_node_configuration: Optional[ControlPlaneNodePatchConfiguration] = ..., 
                kubernetes_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterProperties(_Model):
        aad_configuration: Optional[AadConfiguration]
        administrator_configuration: Optional[AdministratorConfiguration]
        attached_network_ids: Optional[list[str]]
        available_upgrades: Optional[list[AvailableUpgrade]]
        cluster_id: Optional[str]
        connected_cluster_id: Optional[str]
        control_plane_kubernetes_version: Optional[str]
        control_plane_node_configuration: ControlPlaneNodeConfiguration
        detailed_status: Optional[Union[str, KubernetesClusterDetailedStatus]]
        detailed_status_message: Optional[str]
        feature_statuses: Optional[list[FeatureStatus]]
        initial_agent_pool_configurations: list[InitialAgentPoolConfiguration]
        kubernetes_version: str
        managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration]
        network_configuration: NetworkConfiguration
        nodes: Optional[list[KubernetesClusterNode]]
        provisioning_state: Optional[Union[str, KubernetesClusterProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                aad_configuration: Optional[AadConfiguration] = ..., 
                administrator_configuration: Optional[AdministratorConfiguration] = ..., 
                control_plane_node_configuration: ControlPlaneNodeConfiguration, 
                initial_agent_pool_configurations: list[InitialAgentPoolConfiguration], 
                kubernetes_version: str, 
                managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration] = ..., 
                network_configuration: NetworkConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesClusterProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networkcloud.models.KubernetesClusterRestartNodeParameters(_Model):
        node_name: str

        @overload
        def __init__(
                self, 
                *, 
                node_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesLabel(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.KubernetesNodePowerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"
        UNKNOWN = "Unknown"


    class azure.mgmt.networkcloud.models.KubernetesNodeRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTROL_PLANE = "ControlPlane"
        WORKER = "Worker"


    class azure.mgmt.networkcloud.models.KubernetesPluginType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DPDK = "DPDK"
        IPVLAN = "IPVLAN"
        MACVLAN = "MACVLAN"
        OS_DEVICE = "OSDevice"
        SRIOV = "SRIOV"


    class azure.mgmt.networkcloud.models.L2Network(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: L2NetworkProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: L2NetworkProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.L2NetworkAttachmentConfiguration(_Model):
        network_id: str
        plugin_type: Optional[Union[str, KubernetesPluginType]]

        @overload
        def __init__(
                self, 
                *, 
                network_id: str, 
                plugin_type: Optional[Union[str, KubernetesPluginType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.L2NetworkDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.L2NetworkPatchParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.L2NetworkProperties(_Model):
        associated_resource_ids: Optional[list[str]]
        cluster_id: Optional[str]
        detailed_status: Optional[Union[str, L2NetworkDetailedStatus]]
        detailed_status_message: Optional[str]
        hybrid_aks_clusters_associated_ids: Optional[list[str]]
        hybrid_aks_plugin_type: Optional[Union[str, HybridAksPluginType]]
        interface_name: Optional[str]
        l2_isolation_domain_id: str
        provisioning_state: Optional[Union[str, L2NetworkProvisioningState]]
        virtual_machines_associated_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                hybrid_aks_plugin_type: Optional[Union[str, HybridAksPluginType]] = ..., 
                interface_name: Optional[str] = ..., 
                l2_isolation_domain_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.L2NetworkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.L2ServiceLoadBalancerConfiguration(_Model):
        ip_address_pools: Optional[list[IpAddressPool]]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_pools: Optional[list[IpAddressPool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.L3Network(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: L3NetworkProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: L3NetworkProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.L3NetworkAttachmentConfiguration(_Model):
        ipam_enabled: Optional[Union[str, L3NetworkConfigurationIpamEnabled]]
        network_id: str
        plugin_type: Optional[Union[str, KubernetesPluginType]]

        @overload
        def __init__(
                self, 
                *, 
                ipam_enabled: Optional[Union[str, L3NetworkConfigurationIpamEnabled]] = ..., 
                network_id: str, 
                plugin_type: Optional[Union[str, KubernetesPluginType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.L3NetworkConfigurationIpamEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.L3NetworkDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.L3NetworkPatchParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.L3NetworkProperties(_Model):
        associated_resource_ids: Optional[list[str]]
        cluster_id: Optional[str]
        detailed_status: Optional[Union[str, L3NetworkDetailedStatus]]
        detailed_status_message: Optional[str]
        hybrid_aks_clusters_associated_ids: Optional[list[str]]
        hybrid_aks_ipam_enabled: Optional[Union[str, HybridAksIpamEnabled]]
        hybrid_aks_plugin_type: Optional[Union[str, HybridAksPluginType]]
        interface_name: Optional[str]
        ip_allocation_type: Optional[Union[str, IpAllocationType]]
        ipv4_connected_prefix: Optional[str]
        ipv6_connected_prefix: Optional[str]
        l3_isolation_domain_id: str
        provisioning_state: Optional[Union[str, L3NetworkProvisioningState]]
        virtual_machines_associated_ids: Optional[list[str]]
        vlan: int

        @overload
        def __init__(
                self, 
                *, 
                hybrid_aks_ipam_enabled: Optional[Union[str, HybridAksIpamEnabled]] = ..., 
                hybrid_aks_plugin_type: Optional[Union[str, HybridAksPluginType]] = ..., 
                interface_name: Optional[str] = ..., 
                ip_allocation_type: Optional[Union[str, IpAllocationType]] = ..., 
                ipv4_connected_prefix: Optional[str] = ..., 
                ipv6_connected_prefix: Optional[str] = ..., 
                l3_isolation_domain_id: str, 
                vlan: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.L3NetworkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.LldpNeighbor(_Model):
        port_description: Optional[str]
        port_name: Optional[str]
        system_description: Optional[str]
        system_name: Optional[str]


    class azure.mgmt.networkcloud.models.MachineDisk(_Model):
        capacity_gb: Optional[int]
        connection: Optional[Union[str, MachineSkuDiskConnectionType]]
        type: Optional[Union[str, DiskType]]


    class azure.mgmt.networkcloud.models.MachineSkuDiskConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCIE = "PCIE"
        RAID = "RAID"
        SAS = "SAS"
        SATA = "SATA"


    class azure.mgmt.networkcloud.models.MachineSkuProperties(_Model):
        bootstrap_protocol: Optional[Union[str, BootstrapProtocol]]
        cpu_cores: Optional[int]
        cpu_sockets: Optional[int]
        disks: Optional[list[MachineDisk]]
        generation: Optional[str]
        hardware_version: Optional[str]
        memory_capacity_gb: Optional[int]
        model: Optional[str]
        network_interfaces: Optional[list[NetworkInterface]]
        total_threads: Optional[int]
        vendor: Optional[str]


    class azure.mgmt.networkcloud.models.MachineSkuSlot(_Model):
        properties: Optional[MachineSkuProperties]
        rack_slot: Optional[int]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MachineSkuProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.ManagedResourceGroupConfiguration(_Model):
        location: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.networkcloud.models.ManagedServiceIdentitySelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_IDENTITY = "SystemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "UserAssignedIdentity"


    class azure.mgmt.networkcloud.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.networkcloud.models.NetworkAttachment(_Model):
        attached_network_id: str
        default_gateway: Optional[Union[str, DefaultGateway]]
        ip_allocation_method: Union[str, VirtualMachineIPAllocationMethod]
        ipv4_address: Optional[str]
        ipv6_address: Optional[str]
        mac_address: Optional[str]
        network_attachment_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attached_network_id: str, 
                default_gateway: Optional[Union[str, DefaultGateway]] = ..., 
                ip_allocation_method: Union[str, VirtualMachineIPAllocationMethod], 
                ipv4_address: Optional[str] = ..., 
                ipv6_address: Optional[str] = ..., 
                network_attachment_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.NetworkConfiguration(_Model):
        attached_network_configuration: Optional[AttachedNetworkConfiguration]
        bgp_service_load_balancer_configuration: Optional[BgpServiceLoadBalancerConfiguration]
        cloud_services_network_id: str
        cni_network_id: str
        dns_service_ip: Optional[str]
        l2_service_load_balancer_configuration: Optional[L2ServiceLoadBalancerConfiguration]
        pod_cidrs: Optional[list[str]]
        service_cidrs: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                attached_network_configuration: Optional[AttachedNetworkConfiguration] = ..., 
                bgp_service_load_balancer_configuration: Optional[BgpServiceLoadBalancerConfiguration] = ..., 
                cloud_services_network_id: str, 
                cni_network_id: str, 
                dns_service_ip: Optional[str] = ..., 
                l2_service_load_balancer_configuration: Optional[L2ServiceLoadBalancerConfiguration] = ..., 
                pod_cidrs: Optional[list[str]] = ..., 
                service_cidrs: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.NetworkInterface(_Model):
        address: Optional[str]
        device_connection_type: Optional[Union[str, DeviceConnectionType]]
        model: Optional[str]
        physical_slot: Optional[int]
        port_count: Optional[int]
        port_speed: Optional[int]
        vendor: Optional[str]


    class azure.mgmt.networkcloud.models.Nic(_Model):
        lldp_neighbor: Optional[LldpNeighbor]
        mac_address: Optional[str]
        name: Optional[str]


    class azure.mgmt.networkcloud.models.NodePoolAdministratorConfigurationPatch(_Model):
        ssh_public_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                ssh_public_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.Operation(_Model):
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


    class azure.mgmt.networkcloud.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.networkcloud.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        properties: Optional[OperationStatusResultProperties]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OperationStatusResultProperties] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.OperationStatusResultProperties(_Model):
        exit_code: Optional[str]
        output_head: Optional[str]
        result_ref: Optional[str]
        result_url: Optional[str]


    class azure.mgmt.networkcloud.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.networkcloud.models.OsDisk(_Model):
        create_option: Optional[Union[str, OsDiskCreateOption]]
        delete_option: Optional[Union[str, OsDiskDeleteOption]]
        disk_size_gb: int

        @overload
        def __init__(
                self, 
                *, 
                create_option: Optional[Union[str, OsDiskCreateOption]] = ..., 
                delete_option: Optional[Union[str, OsDiskDeleteOption]] = ..., 
                disk_size_gb: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.OsDiskCreateOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EPHEMERAL = "Ephemeral"
        PERSISTENT = "Persistent"


    class azure.mgmt.networkcloud.models.OsDiskDeleteOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"


    class azure.mgmt.networkcloud.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.networkcloud.models.Rack(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: RackProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: RackProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.RackDefinition(_Model):
        availability_zone: Optional[str]
        bare_metal_machine_configuration_data: Optional[list[BareMetalMachineConfigurationData]]
        network_rack_id: str
        rack_location: Optional[str]
        rack_serial_number: str
        rack_sku_id: str
        storage_appliance_configuration_data: Optional[list[StorageApplianceConfigurationData]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                bare_metal_machine_configuration_data: Optional[list[BareMetalMachineConfigurationData]] = ..., 
                network_rack_id: str, 
                rack_location: Optional[str] = ..., 
                rack_serial_number: str, 
                rack_sku_id: str, 
                storage_appliance_configuration_data: Optional[list[StorageApplianceConfigurationData]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.RackDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.RackPatchParameters(_Model):
        properties: Optional[RacksPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RacksPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.RackProperties(_Model):
        availability_zone: str
        cluster_id: Optional[str]
        detailed_status: Optional[Union[str, RackDetailedStatus]]
        detailed_status_message: Optional[str]
        provisioning_state: Optional[Union[str, RackProvisioningState]]
        rack_location: str
        rack_serial_number: str
        rack_sku_id: str

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: str, 
                rack_location: str, 
                rack_serial_number: str, 
                rack_sku_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.RackProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.RackSku(ProxyResource):
        id: str
        name: str
        properties: RackSkuProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: RackSkuProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.RackSkuProperties(_Model):
        compute_machines: Optional[list[MachineSkuSlot]]
        controller_machines: Optional[list[MachineSkuSlot]]
        description: Optional[str]
        max_cluster_slots: Optional[int]
        provisioning_state: Optional[Union[str, RackSkuProvisioningState]]
        rack_type: Optional[Union[str, RackSkuType]]
        storage_appliances: Optional[list[StorageApplianceSkuSlot]]
        supported_rack_sku_ids: Optional[list[str]]


    class azure.mgmt.networkcloud.models.RackSkuProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.RackSkuType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGGREGATOR = "Aggregator"
        COMPUTE = "Compute"
        SINGLE = "Single"


    class azure.mgmt.networkcloud.models.RacksPatchProperties(_Model):
        rack_location: Optional[str]
        rack_serial_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                rack_location: Optional[str] = ..., 
                rack_serial_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.RelayType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLATFORM = "Platform"
        PUBLIC = "Public"


    class azure.mgmt.networkcloud.models.RemoteVendorManagementFeature(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUPPORTED = "Supported"
        UNSUPPORTED = "Unsupported"


    class azure.mgmt.networkcloud.models.RemoteVendorManagementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNSUPPORTED = "Unsupported"


    class azure.mgmt.networkcloud.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.networkcloud.models.RuntimeProtectionConfiguration(_Model):
        enforcement_level: Optional[Union[str, RuntimeProtectionEnforcementLevel]]

        @overload
        def __init__(
                self, 
                *, 
                enforcement_level: Optional[Union[str, RuntimeProtectionEnforcementLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.RuntimeProtectionEnforcementLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        DISABLED = "Disabled"
        ON_DEMAND = "OnDemand"
        PASSIVE = "Passive"
        REAL_TIME = "RealTime"


    class azure.mgmt.networkcloud.models.RuntimeProtectionStatus(_Model):
        definitions_last_updated: Optional[datetime]
        definitions_version: Optional[str]
        scan_completed_time: Optional[datetime]
        scan_scheduled_time: Optional[datetime]
        scan_started_time: Optional[datetime]


    class azure.mgmt.networkcloud.models.SecretArchiveReference(_Model):
        key_vault_id: Optional[str]
        key_vault_uri: Optional[str]
        secret_name: Optional[str]
        secret_version: Optional[str]


    class azure.mgmt.networkcloud.models.SecretArchiveSettings(_Model):
        associated_identity: Optional[IdentitySelector]
        vault_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                associated_identity: Optional[IdentitySelector] = ..., 
                vault_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.SecretRotationStatus(_Model):
        expire_period_days: Optional[int]
        last_rotation_time: Optional[datetime]
        rotation_period_days: Optional[int]
        secret_archive_reference: Optional[SecretArchiveReference]
        secret_type: Optional[str]


    class azure.mgmt.networkcloud.models.ServiceLoadBalancerBgpPeer(_Model):
        bfd_enabled: Optional[Union[str, BfdEnabled]]
        bgp_multi_hop: Optional[Union[str, BgpMultiHop]]
        hold_time: Optional[str]
        keep_alive_time: Optional[str]
        my_asn: Optional[int]
        name: str
        password: Optional[str]
        peer_address: str
        peer_asn: int
        peer_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bfd_enabled: Optional[Union[str, BfdEnabled]] = ..., 
                bgp_multi_hop: Optional[Union[str, BgpMultiHop]] = ..., 
                hold_time: Optional[str] = ..., 
                keep_alive_time: Optional[str] = ..., 
                my_asn: Optional[int] = ..., 
                name: str, 
                password: Optional[str] = ..., 
                peer_address: str, 
                peer_asn: int, 
                peer_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ServicePrincipalInformation(_Model):
        application_id: str
        password: str
        principal_id: str
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                application_id: str, 
                password: str, 
                principal_id: str, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.SkipShutdown(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.SshPublicKey(_Model):
        key_data: str

        @overload
        def __init__(
                self, 
                *, 
                key_data: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StepState(_Model):
        end_time: Optional[str]
        message: Optional[str]
        start_time: Optional[str]
        status: Optional[Union[str, StepStateStatus]]
        step_name: Optional[str]


    class azure.mgmt.networkcloud.models.StepStateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"


    class azure.mgmt.networkcloud.models.StorageAppliance(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: StorageApplianceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: StorageApplianceProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.StorageApplianceCommandSpecification(_Model):
        arguments: Optional[list[str]]
        command: str

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[list[str]] = ..., 
                command: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StorageApplianceConfigurationData(_Model):
        admin_credentials: AdministrativeCredentials
        rack_slot: int
        serial_number: str
        storage_appliance_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_credentials: AdministrativeCredentials, 
                rack_slot: int, 
                serial_number: str, 
                storage_appliance_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StorageApplianceDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEGRADED = "Degraded"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.StorageApplianceEnableRemoteVendorManagementParameters(_Model):
        support_endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                support_endpoints: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StorageAppliancePatchParameters(_Model):
        properties: Optional[StorageAppliancePatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageAppliancePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.StorageAppliancePatchProperties(_Model):
        serial_number: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                serial_number: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StorageApplianceProperties(_Model):
        administrator_credentials: AdministrativeCredentials
        ca_certificate: Optional[CertificateInfo]
        capacity: Optional[int]
        capacity_used: Optional[int]
        cluster_id: Optional[str]
        detailed_status: Optional[Union[str, StorageApplianceDetailedStatus]]
        detailed_status_message: Optional[str]
        management_ipv4_address: Optional[str]
        manufacturer: Optional[str]
        model: Optional[str]
        provisioning_state: Optional[Union[str, StorageApplianceProvisioningState]]
        rack_id: str
        rack_slot: int
        remote_vendor_management_feature: Optional[Union[str, RemoteVendorManagementFeature]]
        remote_vendor_management_status: Optional[Union[str, RemoteVendorManagementStatus]]
        secret_rotation_status: Optional[list[SecretRotationStatus]]
        serial_number: str
        storage_appliance_sku_id: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                administrator_credentials: AdministrativeCredentials, 
                rack_id: str, 
                rack_slot: int, 
                serial_number: str, 
                storage_appliance_sku_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StorageApplianceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.StorageApplianceRunReadCommandsParameters(_Model):
        commands: list[StorageApplianceCommandSpecification]
        limit_time_seconds: int

        @overload
        def __init__(
                self, 
                *, 
                commands: list[StorageApplianceCommandSpecification], 
                limit_time_seconds: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StorageApplianceSkuProperties(_Model):
        capacity_gb: Optional[int]
        model: Optional[str]


    class azure.mgmt.networkcloud.models.StorageApplianceSkuSlot(_Model):
        properties: Optional[StorageApplianceSkuProperties]
        rack_slot: Optional[int]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageApplianceSkuProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.StorageProfile(_Model):
        os_disk: OsDisk
        volume_attachments: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                os_disk: OsDisk, 
                volume_attachments: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.StringKeyValuePair(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.SystemData(_Model):
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


    class azure.mgmt.networkcloud.models.TrackedResource(Resource):
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


    class azure.mgmt.networkcloud.models.TrunkedNetwork(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: TrunkedNetworkProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: TrunkedNetworkProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.TrunkedNetworkAttachmentConfiguration(_Model):
        network_id: str
        plugin_type: Optional[Union[str, KubernetesPluginType]]

        @overload
        def __init__(
                self, 
                *, 
                network_id: str, 
                plugin_type: Optional[Union[str, KubernetesPluginType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.TrunkedNetworkDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.TrunkedNetworkPatchParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.TrunkedNetworkProperties(_Model):
        associated_resource_ids: Optional[list[str]]
        cluster_id: Optional[str]
        detailed_status: Optional[Union[str, TrunkedNetworkDetailedStatus]]
        detailed_status_message: Optional[str]
        hybrid_aks_clusters_associated_ids: Optional[list[str]]
        hybrid_aks_plugin_type: Optional[Union[str, HybridAksPluginType]]
        interface_name: Optional[str]
        isolation_domain_ids: list[str]
        provisioning_state: Optional[Union[str, TrunkedNetworkProvisioningState]]
        virtual_machines_associated_ids: Optional[list[str]]
        vlans: list[int]

        @overload
        def __init__(
                self, 
                *, 
                hybrid_aks_plugin_type: Optional[Union[str, HybridAksPluginType]] = ..., 
                interface_name: Optional[str] = ..., 
                isolation_domain_ids: list[str], 
                vlans: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.TrunkedNetworkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.networkcloud.models.ValidationThreshold(_Model):
        grouping: Union[str, ValidationThresholdGrouping]
        type: Union[str, ValidationThresholdType]
        value: int

        @overload
        def __init__(
                self, 
                *, 
                grouping: Union[str, ValidationThresholdGrouping], 
                type: Union[str, ValidationThresholdType], 
                value: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.ValidationThresholdGrouping(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PER_CLUSTER = "PerCluster"
        PER_RACK = "PerRack"


    class azure.mgmt.networkcloud.models.ValidationThresholdType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT_SUCCESS = "CountSuccess"
        PERCENT_SUCCESS = "PercentSuccess"


    class azure.mgmt.networkcloud.models.VirtualMachine(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: VirtualMachineProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: VirtualMachineProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.VirtualMachineAssignRelayParameters(_Model):
        machine_id: str
        relay_type: Optional[Union[str, RelayType]]

        @overload
        def __init__(
                self, 
                *, 
                machine_id: str, 
                relay_type: Optional[Union[str, RelayType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VirtualMachineBootMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIOS = "BIOS"
        UEFI = "UEFI"


    class azure.mgmt.networkcloud.models.VirtualMachineDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        ERROR = "Error"
        PROVISIONING = "Provisioning"
        RUNNING = "Running"
        SCHEDULING = "Scheduling"
        STOPPED = "Stopped"
        TERMINATING = "Terminating"
        UNKNOWN = "Unknown"


    class azure.mgmt.networkcloud.models.VirtualMachineDeviceModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        T1 = "T1"
        T2 = "T2"
        T3 = "T3"


    class azure.mgmt.networkcloud.models.VirtualMachineIPAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.networkcloud.models.VirtualMachineIsolateEmulatorThread(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


    class azure.mgmt.networkcloud.models.VirtualMachinePatchParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[VirtualMachinePatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[VirtualMachinePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.VirtualMachinePatchProperties(_Model):
        vm_image_repository_credentials: Optional[ImageRepositoryCredentials]

        @overload
        def __init__(
                self, 
                *, 
                vm_image_repository_credentials: Optional[ImageRepositoryCredentials] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VirtualMachinePlacementHint(_Model):
        hint_type: Union[str, VirtualMachinePlacementHintType]
        resource_id: str
        scheduling_execution: Union[str, VirtualMachineSchedulingExecution]
        scope: Union[str, VirtualMachinePlacementHintPodAffinityScope]

        @overload
        def __init__(
                self, 
                *, 
                hint_type: Union[str, VirtualMachinePlacementHintType], 
                resource_id: str, 
                scheduling_execution: Union[str, VirtualMachineSchedulingExecution], 
                scope: Union[str, VirtualMachinePlacementHintPodAffinityScope]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VirtualMachinePlacementHintPodAffinityScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MACHINE = "Machine"
        RACK = "Rack"


    class azure.mgmt.networkcloud.models.VirtualMachinePlacementHintType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFFINITY = "Affinity"
        ANTI_AFFINITY = "AntiAffinity"


    class azure.mgmt.networkcloud.models.VirtualMachinePowerOffParameters(_Model):
        skip_shutdown: Optional[Union[str, SkipShutdown]]

        @overload
        def __init__(
                self, 
                *, 
                skip_shutdown: Optional[Union[str, SkipShutdown]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VirtualMachinePowerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF = "Off"
        ON = "On"
        UNKNOWN = "Unknown"


    class azure.mgmt.networkcloud.models.VirtualMachineProperties(_Model):
        admin_username: str
        availability_zone: Optional[str]
        bare_metal_machine_id: Optional[str]
        boot_method: Optional[Union[str, VirtualMachineBootMethod]]
        cloud_services_network_attachment: NetworkAttachment
        cluster_id: Optional[str]
        console_extended_location: Optional[ExtendedLocation]
        cpu_cores: int
        detailed_status: Optional[Union[str, VirtualMachineDetailedStatus]]
        detailed_status_message: Optional[str]
        isolate_emulator_thread: Optional[Union[str, VirtualMachineIsolateEmulatorThread]]
        memory_size_gb: int
        network_attachments: Optional[list[NetworkAttachment]]
        network_data: Optional[str]
        network_data_content: Optional[str]
        placement_hints: Optional[list[VirtualMachinePlacementHint]]
        power_state: Optional[Union[str, VirtualMachinePowerState]]
        provisioning_state: Optional[Union[str, VirtualMachineProvisioningState]]
        ssh_public_keys: Optional[list[SshPublicKey]]
        storage_profile: StorageProfile
        user_data: Optional[str]
        user_data_content: Optional[str]
        virtio_interface: Optional[Union[str, VirtualMachineVirtioInterfaceType]]
        vm_device_model: Optional[Union[str, VirtualMachineDeviceModelType]]
        vm_image: str
        vm_image_repository_credentials: Optional[ImageRepositoryCredentials]
        volumes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                admin_username: str, 
                boot_method: Optional[Union[str, VirtualMachineBootMethod]] = ..., 
                cloud_services_network_attachment: NetworkAttachment, 
                console_extended_location: Optional[ExtendedLocation] = ..., 
                cpu_cores: int, 
                isolate_emulator_thread: Optional[Union[str, VirtualMachineIsolateEmulatorThread]] = ..., 
                memory_size_gb: int, 
                network_attachments: Optional[list[NetworkAttachment]] = ..., 
                network_data: Optional[str] = ..., 
                network_data_content: Optional[str] = ..., 
                placement_hints: Optional[list[VirtualMachinePlacementHint]] = ..., 
                ssh_public_keys: Optional[list[SshPublicKey]] = ..., 
                storage_profile: StorageProfile, 
                user_data: Optional[str] = ..., 
                user_data_content: Optional[str] = ..., 
                virtio_interface: Optional[Union[str, VirtualMachineVirtioInterfaceType]] = ..., 
                vm_device_model: Optional[Union[str, VirtualMachineDeviceModelType]] = ..., 
                vm_image: str, 
                vm_image_repository_credentials: Optional[ImageRepositoryCredentials] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VirtualMachineProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.VirtualMachineSchedulingExecution(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HARD = "Hard"
        SOFT = "Soft"


    class azure.mgmt.networkcloud.models.VirtualMachineVirtioInterfaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODERN = "Modern"
        TRANSITIONAL = "Transitional"


    class azure.mgmt.networkcloud.models.Volume(TrackedResource):
        etag: Optional[str]
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: VolumeProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: VolumeProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkcloud.models.VolumeDetailedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ERROR = "Error"
        PROVISIONING = "Provisioning"


    class azure.mgmt.networkcloud.models.VolumePatchParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VolumeProperties(_Model):
        allocated_size_mi_b: Optional[int]
        attached_to: Optional[list[str]]
        detailed_status: Optional[Union[str, VolumeDetailedStatus]]
        detailed_status_message: Optional[str]
        provisioning_state: Optional[Union[str, VolumeProvisioningState]]
        serial_number: Optional[str]
        size_mi_b: int
        storage_appliance_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                size_mi_b: int, 
                storage_appliance_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VolumeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networkcloud.models.VulnerabilityScanningSettings(_Model):
        container_scan: Optional[Union[str, VulnerabilityScanningSettingsContainerScan]]

        @overload
        def __init__(
                self, 
                *, 
                container_scan: Optional[Union[str, VulnerabilityScanningSettingsContainerScan]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.VulnerabilityScanningSettingsContainerScan(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.networkcloud.models.VulnerabilityScanningSettingsPatch(_Model):
        container_scan: Optional[Union[str, VulnerabilityScanningSettingsContainerScan]]

        @overload
        def __init__(
                self, 
                *, 
                container_scan: Optional[Union[str, VulnerabilityScanningSettingsContainerScan]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkcloud.models.WorkloadImpact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"


namespace azure.mgmt.networkcloud.operations

    class azure.mgmt.networkcloud.operations.AgentPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_parameters: AgentPool, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_update_parameters: Optional[AgentPoolPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                agent_pool_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentPool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                agent_pool_name: str, 
                **kwargs: Any
            ) -> AgentPool: ...

        @distributed_trace
        def list_by_kubernetes_cluster(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentPool]: ...


    class azure.mgmt.networkcloud.operations.BareMetalMachineKeySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_parameters: BareMetalMachineKeySet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachineKeySet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachineKeySet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachineKeySet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_update_parameters: Optional[BareMetalMachineKeySetPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachineKeySet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachineKeySet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                bare_metal_machine_key_set_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachineKeySet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bare_metal_machine_key_set_name: str, 
                **kwargs: Any
            ) -> BareMetalMachineKeySet: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BareMetalMachineKeySet]: ...


    class azure.mgmt.networkcloud.operations.BareMetalMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_cordon_parameters: Optional[BareMetalMachineCordonParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_cordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_cordon_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_cordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_cordon_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_parameters: BareMetalMachine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachine]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_power_off_parameters: Optional[BareMetalMachinePowerOffParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_power_off_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_power_off_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_reimage(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_replace(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_replace_parameters: Optional[BareMetalMachineReplaceParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_replace(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_replace_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_replace(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_replace_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_command_parameters: BareMetalMachineRunCommandParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_command_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_command_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_data_extracts(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_parameters: BareMetalMachineRunDataExtractsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_data_extracts(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_data_extracts(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_data_extracts_restricted(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_restricted_parameters: BareMetalMachineRunDataExtractsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_data_extracts_restricted(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_restricted_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_data_extracts_restricted(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_data_extracts_restricted_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_read_commands_parameters: BareMetalMachineRunReadCommandsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_read_commands_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_run_read_commands_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_uncordon(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_update_parameters: Optional[BareMetalMachinePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                bare_metal_machine_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BareMetalMachine]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                bare_metal_machine_name: str, 
                **kwargs: Any
            ) -> BareMetalMachine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BareMetalMachine]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BareMetalMachine]: ...


    class azure.mgmt.networkcloud.operations.BmcKeySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_parameters: BmcKeySet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BmcKeySet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BmcKeySet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BmcKeySet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_update_parameters: Optional[BmcKeySetPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BmcKeySet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BmcKeySet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                bmc_key_set_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[BmcKeySet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                bmc_key_set_name: str, 
                **kwargs: Any
            ) -> BmcKeySet: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[BmcKeySet]: ...


    class azure.mgmt.networkcloud.operations.CloudServicesNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_parameters: CloudServicesNetwork, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[CloudServicesNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[CloudServicesNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[CloudServicesNetwork]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_update_parameters: Optional[CloudServicesNetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[CloudServicesNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[CloudServicesNetwork]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                cloud_services_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[CloudServicesNetwork]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_services_network_name: str, 
                **kwargs: Any
            ) -> CloudServicesNetwork: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CloudServicesNetwork]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CloudServicesNetwork]: ...


    class azure.mgmt.networkcloud.operations.ClusterManagersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_parameters: ClusterManager, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterManager]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterManager]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterManager]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                **kwargs: Any
            ) -> ClusterManager: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ClusterManager]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ClusterManager]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_update_parameters: Optional[ClusterManagerPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClusterManager: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClusterManager: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_manager_name: str, 
                cluster_manager_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ClusterManager: ...


    class azure.mgmt.networkcloud.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_continue_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_continue_update_version_parameters: ClusterContinueUpdateVersionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_continue_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_continue_update_version_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_continue_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_continue_update_version_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_deploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_deploy_parameters: Optional[ClusterDeployParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_deploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_deploy_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_deploy(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_deploy_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_scan_runtime(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_scan_runtime_parameters: Optional[ClusterScanRuntimeParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_scan_runtime(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_scan_runtime_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_scan_runtime(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_scan_runtime_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_parameters: Optional[ClusterPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_version_parameters: ClusterUpdateVersionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_version_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update_version(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster_update_version_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...


    class azure.mgmt.networkcloud.operations.ConsolesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_parameters: Console, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Console]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Console]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Console]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_update_parameters: Optional[ConsolePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Console]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Console]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                console_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Console]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                console_name: str, 
                **kwargs: Any
            ) -> Console: ...

        @distributed_trace
        def list_by_virtual_machine(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Console]: ...


    class azure.mgmt.networkcloud.operations.KubernetesClusterFeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_parameters: KubernetesClusterFeature, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesClusterFeature]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesClusterFeature]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesClusterFeature]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_update_parameters: Optional[KubernetesClusterFeaturePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesClusterFeature]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesClusterFeature]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                kubernetes_cluster_feature_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesClusterFeature]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                feature_name: str, 
                **kwargs: Any
            ) -> KubernetesClusterFeature: ...

        @distributed_trace
        def list_by_kubernetes_cluster(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[KubernetesClusterFeature]: ...


    class azure.mgmt.networkcloud.operations.KubernetesClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_parameters: KubernetesCluster, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_restart_node(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_restart_node_parameters: KubernetesClusterRestartNodeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_restart_node(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_restart_node_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_restart_node(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_restart_node_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_update_parameters: Optional[KubernetesClusterPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesCluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                kubernetes_cluster_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[KubernetesCluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                kubernetes_cluster_name: str, 
                **kwargs: Any
            ) -> KubernetesCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[KubernetesCluster]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[KubernetesCluster]: ...


    class azure.mgmt.networkcloud.operations.L2NetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_parameters: L2Network, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[L2Network]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[L2Network]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[L2Network]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                **kwargs: Any
            ) -> L2Network: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[L2Network]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[L2Network]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_update_parameters: Optional[L2NetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L2Network: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L2Network: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                l2_network_name: str, 
                l2_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L2Network: ...


    class azure.mgmt.networkcloud.operations.L3NetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_parameters: L3Network, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[L3Network]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[L3Network]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[L3Network]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                **kwargs: Any
            ) -> L3Network: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[L3Network]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[L3Network]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_update_parameters: Optional[L3NetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L3Network: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L3Network: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                l3_network_name: str, 
                l3_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> L3Network: ...


    class azure.mgmt.networkcloud.operations.MetricsConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_parameters: ClusterMetricsConfiguration, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterMetricsConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterMetricsConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterMetricsConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_update_parameters: Optional[ClusterMetricsConfigurationPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterMetricsConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterMetricsConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                metrics_configuration_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ClusterMetricsConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                metrics_configuration_name: str, 
                **kwargs: Any
            ) -> ClusterMetricsConfiguration: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ClusterMetricsConfiguration]: ...


    class azure.mgmt.networkcloud.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.networkcloud.operations.RackSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                rack_sku_name: str, 
                **kwargs: Any
            ) -> RackSku: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[RackSku]: ...


    class azure.mgmt.networkcloud.operations.RacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_parameters: Rack, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Rack]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Rack]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Rack]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_update_parameters: Optional[RackPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Rack]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Rack]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                rack_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Rack]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                rack_name: str, 
                **kwargs: Any
            ) -> Rack: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Rack]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Rack]: ...


    class azure.mgmt.networkcloud.operations.StorageAppliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_parameters: StorageAppliance, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[StorageAppliance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[StorageAppliance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[StorageAppliance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_disable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_enable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_enable_remote_vendor_management_parameters: Optional[StorageApplianceEnableRemoteVendorManagementParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_enable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_enable_remote_vendor_management_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_enable_remote_vendor_management(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_enable_remote_vendor_management_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_run_read_commands_parameters: StorageApplianceRunReadCommandsParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_run_read_commands_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_run_read_commands(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_run_read_commands_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_update_parameters: Optional[StorageAppliancePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[StorageAppliance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[StorageAppliance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                storage_appliance_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[StorageAppliance]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_appliance_name: str, 
                **kwargs: Any
            ) -> StorageAppliance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[StorageAppliance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[StorageAppliance]: ...


    class azure.mgmt.networkcloud.operations.TrunkedNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_parameters: TrunkedNetwork, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[TrunkedNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[TrunkedNetwork]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[TrunkedNetwork]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                **kwargs: Any
            ) -> TrunkedNetwork: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TrunkedNetwork]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TrunkedNetwork]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_update_parameters: Optional[TrunkedNetworkPatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> TrunkedNetwork: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> TrunkedNetwork: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                trunked_network_name: str, 
                trunked_network_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> TrunkedNetwork: ...


    class azure.mgmt.networkcloud.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_assign_relay(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_assign_relay_parameters: Optional[VirtualMachineAssignRelayParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_assign_relay(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_assign_relay_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_assign_relay(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_assign_relay_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_parameters: VirtualMachine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_power_off_parameters: Optional[VirtualMachinePowerOffParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_power_off_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_power_off_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_reimage(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_update_parameters: Optional[VirtualMachinePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                virtual_machine_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                virtual_machine_name: str, 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...


    class azure.mgmt.networkcloud.operations.VolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_parameters: Volume, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Volume]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Volume]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_update_parameters: Optional[VolumePatchParameters] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Volume: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_update_parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Volume: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                volume_name: str, 
                volume_update_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> Volume: ...


```