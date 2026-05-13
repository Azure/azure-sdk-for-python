```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.containerservicefleet

    class azure.mgmt.containerservicefleet.ContainerServiceFleetMgmtClient: implements ContextManager 
        auto_upgrade_profile_operations: AutoUpgradeProfileOperationsOperations
        auto_upgrade_profiles: AutoUpgradeProfilesOperations
        fleet_managed_namespaces: FleetManagedNamespacesOperations
        fleet_members: FleetMembersOperations
        fleet_update_strategies: FleetUpdateStrategiesOperations
        fleets: FleetsOperations
        gates: GatesOperations
        operations: Operations
        update_runs: UpdateRunsOperations

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


namespace azure.mgmt.containerservicefleet.aio

    class azure.mgmt.containerservicefleet.aio.ContainerServiceFleetMgmtClient: implements AsyncContextManager 
        auto_upgrade_profile_operations: AutoUpgradeProfileOperationsOperations
        auto_upgrade_profiles: AutoUpgradeProfilesOperations
        fleet_managed_namespaces: FleetManagedNamespacesOperations
        fleet_members: FleetMembersOperations
        fleet_update_strategies: FleetUpdateStrategiesOperations
        fleets: FleetsOperations
        gates: GatesOperations
        operations: Operations
        update_runs: UpdateRunsOperations

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


namespace azure.mgmt.containerservicefleet.aio.operations

    class azure.mgmt.containerservicefleet.aio.operations.AutoUpgradeProfileOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-01', params_added_on={'2025-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'accept']}, api_versions_list=['2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def begin_generate_update_run(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateResponse]: ...


    class azure.mgmt.containerservicefleet.aio.operations.AutoUpgradeProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                resource: AutoUpgradeProfile, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoUpgradeProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoUpgradeProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AutoUpgradeProfile]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-02-preview', params_added_on={'2024-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'etag', 'match_condition']}, api_versions_list=['2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-05-02-preview', params_added_on={'2024-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'accept']}, api_versions_list=['2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                **kwargs: Any
            ) -> AutoUpgradeProfile: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-02-preview', params_added_on={'2024-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'top', 'skip_token', 'accept']}, api_versions_list=['2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AutoUpgradeProfile]: ...


    class azure.mgmt.containerservicefleet.aio.operations.FleetManagedNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                resource: FleetManagedNamespace, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetManagedNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetManagedNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetManagedNamespace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01-preview', params_added_on={'2025-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'managed_namespace_name', 'etag', 'match_condition']}, api_versions_list=['2025-08-01-preview', '2026-02-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                properties: FleetManagedNamespacePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetManagedNamespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetManagedNamespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetManagedNamespace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01-preview', params_added_on={'2025-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'managed_namespace_name', 'accept']}, api_versions_list=['2025-08-01-preview', '2026-02-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> FleetManagedNamespace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01-preview', params_added_on={'2025-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'accept']}, api_versions_list=['2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FleetManagedNamespace]: ...


    class azure.mgmt.containerservicefleet.aio.operations.FleetMembersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                resource: FleetMember, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetMember]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetMember]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetMember]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                properties: FleetMemberUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetMember]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetMember]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetMember]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                **kwargs: Any
            ) -> FleetMember: ...

        @distributed_trace
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FleetMember]: ...


    class azure.mgmt.containerservicefleet.aio.operations.FleetUpdateStrategiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                resource: FleetUpdateStrategy, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetUpdateStrategy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetUpdateStrategy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[FleetUpdateStrategy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-08-15-preview', params_added_on={'2023-08-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_strategy_name', 'etag', 'match_condition']}, api_versions_list=['2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-08-15-preview', params_added_on={'2023-08-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_strategy_name', 'accept']}, api_versions_list=['2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                **kwargs: Any
            ) -> FleetUpdateStrategy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-08-15-preview', params_added_on={'2023-08-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'top', 'skip_token', 'accept']}, api_versions_list=['2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[FleetUpdateStrategy]: ...


    class azure.mgmt.containerservicefleet.aio.operations.FleetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: Fleet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: FleetPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> Fleet: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Fleet]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Fleet]: ...

        @distributed_trace_async
        async def list_credentials(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> FleetCredentialResults: ...


    class azure.mgmt.containerservicefleet.aio.operations.GatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                properties: GatePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Gate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Gate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Gate]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'gate_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                **kwargs: Any
            ) -> Gate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'filter', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Gate]: ...


    class azure.mgmt.containerservicefleet.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.containerservicefleet.aio.operations.UpdateRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                resource: UpdateRun, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'etag', 'match_condition']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_skip(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                body: SkipProperties, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @overload
        async def begin_skip(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @overload
        async def begin_skip(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'accept', 'etag', 'match_condition']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def begin_start(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'accept', 'etag', 'match_condition']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def begin_stop(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateRun]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'accept']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                **kwargs: Any
            ) -> UpdateRun: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'top', 'skip_token', 'accept']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateRun]: ...


namespace azure.mgmt.containerservicefleet.models

    class azure.mgmt.containerservicefleet.models.APIServerAccessProfile(_Model):
        enable_private_cluster: Optional[bool]
        enable_vnet_integration: Optional[bool]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_private_cluster: Optional[bool] = ..., 
                enable_vnet_integration: Optional[bool] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.containerservicefleet.models.AdoptionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_IDENTICAL = "IfIdentical"
        NEVER = "Never"


    class azure.mgmt.containerservicefleet.models.Affinity(_Model):
        cluster_affinity: Optional[ClusterAffinity]

        @overload
        def __init__(
                self, 
                *, 
                cluster_affinity: Optional[ClusterAffinity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.AgentProfile(_Model):
        subnet_id: Optional[str]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: Optional[str] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.AutoUpgradeLastTriggerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerservicefleet.models.AutoUpgradeNodeImageSelection(_Model):
        type: Union[str, AutoUpgradeNodeImageSelectionType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, AutoUpgradeNodeImageSelectionType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.AutoUpgradeNodeImageSelectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSISTENT = "Consistent"
        LATEST = "Latest"


    class azure.mgmt.containerservicefleet.models.AutoUpgradeProfile(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[AutoUpgradeProfileProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AutoUpgradeProfileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.AutoUpgradeProfileProperties(_Model):
        auto_upgrade_profile_status: Optional[AutoUpgradeProfileStatus]
        channel: Union[str, UpgradeChannel]
        disabled: Optional[bool]
        long_term_support: Optional[bool]
        node_image_selection: Optional[AutoUpgradeNodeImageSelection]
        provisioning_state: Optional[Union[str, AutoUpgradeProfileProvisioningState]]
        target_kubernetes_version: Optional[str]
        update_strategy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_profile_status: Optional[AutoUpgradeProfileStatus] = ..., 
                channel: Union[str, UpgradeChannel], 
                disabled: Optional[bool] = ..., 
                long_term_support: Optional[bool] = ..., 
                node_image_selection: Optional[AutoUpgradeNodeImageSelection] = ..., 
                target_kubernetes_version: Optional[str] = ..., 
                update_strategy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.AutoUpgradeProfileProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerservicefleet.models.AutoUpgradeProfileStatus(_Model):
        last_trigger_error: Optional[ErrorDetail]
        last_trigger_status: Optional[Union[str, AutoUpgradeLastTriggerStatus]]
        last_trigger_upgrade_versions: Optional[list[str]]
        last_triggered_at: Optional[datetime]


    class azure.mgmt.containerservicefleet.models.ClusterAffinity(_Model):
        required_during_scheduling_ignored_during_execution: Optional[ClusterSelector]

        @overload
        def __init__(
                self, 
                *, 
                required_during_scheduling_ignored_during_execution: Optional[ClusterSelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ClusterResourcePlacementSpec(_Model):
        policy: Optional[PlacementPolicy]

        @overload
        def __init__(
                self, 
                *, 
                policy: Optional[PlacementPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ClusterSelector(_Model):
        cluster_selector_terms: list[ClusterSelectorTerm]

        @overload
        def __init__(
                self, 
                *, 
                cluster_selector_terms: list[ClusterSelectorTerm]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ClusterSelectorTerm(_Model):
        label_selector: Optional[LabelSelector]
        property_selector: Optional[PropertySelector]

        @overload
        def __init__(
                self, 
                *, 
                label_selector: Optional[LabelSelector] = ..., 
                property_selector: Optional[PropertySelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerservicefleet.models.DeletePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        KEEP = "Keep"


    class azure.mgmt.containerservicefleet.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerservicefleet.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerservicefleet.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.Fleet(TrackedResource):
        e_tag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[FleetProperties]
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
                properties: Optional[FleetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetCredentialResult(_Model):
        name: Optional[str]
        value: Optional[bytes]


    class azure.mgmt.containerservicefleet.models.FleetCredentialResults(_Model):
        kubeconfigs: Optional[list[FleetCredentialResult]]


    class azure.mgmt.containerservicefleet.models.FleetHubProfile(_Model):
        agent_profile: Optional[AgentProfile]
        api_server_access_profile: Optional[APIServerAccessProfile]
        dns_prefix: Optional[str]
        fqdn: Optional[str]
        kubernetes_version: Optional[str]
        portal_fqdn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_profile: Optional[AgentProfile] = ..., 
                api_server_access_profile: Optional[APIServerAccessProfile] = ..., 
                dns_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetManagedNamespace(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[FleetManagedNamespaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[FleetManagedNamespaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetManagedNamespacePatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetManagedNamespaceProperties(_Model):
        adoption_policy: Union[str, AdoptionPolicy]
        delete_policy: Union[str, DeletePolicy]
        managed_namespace_properties: Optional[ManagedNamespaceProperties]
        portal_fqdn: Optional[str]
        propagation_policy: Optional[PropagationPolicy]
        provisioning_state: Optional[Union[str, FleetManagedNamespaceProvisioningState]]
        status: Optional[FleetManagedNamespaceStatus]

        @overload
        def __init__(
                self, 
                *, 
                adoption_policy: Union[str, AdoptionPolicy], 
                delete_policy: Union[str, DeletePolicy], 
                managed_namespace_properties: Optional[ManagedNamespaceProperties] = ..., 
                propagation_policy: Optional[PropagationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetManagedNamespaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservicefleet.models.FleetManagedNamespaceStatus(_Model):
        last_operation_error: Optional[ErrorDetail]
        last_operation_id: Optional[str]


    class azure.mgmt.containerservicefleet.models.FleetMember(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[FleetMemberProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetMemberProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetMemberProperties(_Model):
        cluster_resource_id: str
        group: Optional[str]
        labels: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, FleetMemberProvisioningState]]
        status: Optional[FleetMemberStatus]

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: str, 
                group: Optional[str] = ..., 
                labels: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetMemberProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        JOINING = "Joining"
        LEAVING = "Leaving"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservicefleet.models.FleetMemberStatus(_Model):
        last_operation_error: Optional[ErrorDetail]
        last_operation_id: Optional[str]


    class azure.mgmt.containerservicefleet.models.FleetMemberUpdate(_Model):
        properties: Optional[FleetMemberUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetMemberUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetMemberUpdateProperties(_Model):
        group: Optional[str]
        labels: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                group: Optional[str] = ..., 
                labels: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetPatch(_Model):
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


    class azure.mgmt.containerservicefleet.models.FleetProperties(_Model):
        hub_profile: Optional[FleetHubProfile]
        provisioning_state: Optional[Union[str, FleetProvisioningState]]
        status: Optional[FleetStatus]

        @overload
        def __init__(
                self, 
                *, 
                hub_profile: Optional[FleetHubProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerservicefleet.models.FleetStatus(_Model):
        last_operation_error: Optional[ErrorDetail]
        last_operation_id: Optional[str]


    class azure.mgmt.containerservicefleet.models.FleetUpdateStrategy(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[FleetUpdateStrategyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FleetUpdateStrategyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetUpdateStrategyProperties(_Model):
        provisioning_state: Optional[Union[str, FleetUpdateStrategyProvisioningState]]
        strategy: UpdateRunStrategy

        @overload
        def __init__(
                self, 
                *, 
                strategy: UpdateRunStrategy
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.FleetUpdateStrategyProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerservicefleet.models.Gate(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[GateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.GateConfiguration(_Model):
        display_name: Optional[str]
        type: Union[str, GateType]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                type: Union[str, GateType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.GatePatch(_Model):
        properties: GatePatchProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: GatePatchProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.GatePatchProperties(_Model):
        state: Union[str, GateState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, GateState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.GateProperties(_Model):
        display_name: Optional[str]
        gate_type: Union[str, GateType]
        provisioning_state: Optional[Union[str, GateProvisioningState]]
        state: Union[str, GateState]
        target: GateTarget

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                gate_type: Union[str, GateType], 
                state: Union[str, GateState], 
                target: GateTarget
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.GateProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerservicefleet.models.GateState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        PENDING = "Pending"
        SKIPPED = "Skipped"


    class azure.mgmt.containerservicefleet.models.GateTarget(_Model):
        id: str
        update_run_properties: Optional[UpdateRunGateTargetProperties]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                update_run_properties: Optional[UpdateRunGateTargetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.GateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVAL = "Approval"


    class azure.mgmt.containerservicefleet.models.GenerateResponse(_Model):
        id: str


    class azure.mgmt.containerservicefleet.models.LabelSelector(_Model):
        match_expressions: Optional[list[LabelSelectorRequirement]]
        match_labels: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                match_expressions: Optional[list[LabelSelectorRequirement]] = ..., 
                match_labels: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.LabelSelectorOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOES_NOT_EXIST = "DoesNotExist"
        EXISTS = "Exists"
        IN = "In"
        NOT_IN = "NotIn"


    class azure.mgmt.containerservicefleet.models.LabelSelectorRequirement(_Model):
        key: str
        operator: Union[str, LabelSelectorOperator]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                operator: Union[str, LabelSelectorOperator], 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ManagedClusterUpdate(_Model):
        node_image_selection: Optional[NodeImageSelection]
        upgrade: ManagedClusterUpgradeSpec

        @overload
        def __init__(
                self, 
                *, 
                node_image_selection: Optional[NodeImageSelection] = ..., 
                upgrade: ManagedClusterUpgradeSpec
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ManagedClusterUpgradeSpec(_Model):
        kubernetes_version: Optional[str]
        type: Union[str, ManagedClusterUpgradeType]

        @overload
        def __init__(
                self, 
                *, 
                kubernetes_version: Optional[str] = ..., 
                type: Union[str, ManagedClusterUpgradeType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ManagedClusterUpgradeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTROL_PLANE_ONLY = "ControlPlaneOnly"
        FULL = "Full"
        NODE_IMAGE_ONLY = "NodeImageOnly"


    class azure.mgmt.containerservicefleet.models.ManagedNamespaceProperties(_Model):
        annotations: Optional[dict[str, str]]
        default_network_policy: Optional[NetworkPolicy]
        default_resource_quota: Optional[ResourceQuota]
        labels: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                annotations: Optional[dict[str, str]] = ..., 
                default_network_policy: Optional[NetworkPolicy] = ..., 
                default_resource_quota: Optional[ResourceQuota] = ..., 
                labels: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.containerservicefleet.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerservicefleet.models.MemberUpdateStatus(_Model):
        cluster_resource_id: Optional[str]
        message: Optional[str]
        name: Optional[str]
        operation_id: Optional[str]
        status: Optional[UpdateStatus]


    class azure.mgmt.containerservicefleet.models.NetworkPolicy(_Model):
        egress: Optional[Union[str, PolicyRule]]
        ingress: Optional[Union[str, PolicyRule]]

        @overload
        def __init__(
                self, 
                *, 
                egress: Optional[Union[str, PolicyRule]] = ..., 
                ingress: Optional[Union[str, PolicyRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.NodeImageSelection(_Model):
        custom_node_image_versions: Optional[list[NodeImageVersion]]
        type: Union[str, NodeImageSelectionType]

        @overload
        def __init__(
                self, 
                *, 
                custom_node_image_versions: Optional[list[NodeImageVersion]] = ..., 
                type: Union[str, NodeImageSelectionType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.NodeImageSelectionStatus(_Model):
        selected_node_image_versions: Optional[list[NodeImageVersion]]


    class azure.mgmt.containerservicefleet.models.NodeImageSelectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSISTENT = "Consistent"
        CUSTOM = "Custom"
        LATEST = "Latest"


    class azure.mgmt.containerservicefleet.models.NodeImageVersion(_Model):
        version: Optional[str]


    class azure.mgmt.containerservicefleet.models.Operation(_Model):
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


    class azure.mgmt.containerservicefleet.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.containerservicefleet.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.containerservicefleet.models.PlacementPolicy(_Model):
        affinity: Optional[Affinity]
        cluster_names: Optional[list[str]]
        placement_type: Optional[Union[str, PlacementType]]
        tolerations: Optional[list[Toleration]]

        @overload
        def __init__(
                self, 
                *, 
                affinity: Optional[Affinity] = ..., 
                cluster_names: Optional[list[str]] = ..., 
                placement_type: Optional[Union[str, PlacementType]] = ..., 
                tolerations: Optional[list[Toleration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.PlacementProfile(_Model):
        default_cluster_resource_placement: Optional[ClusterResourcePlacementSpec]

        @overload
        def __init__(
                self, 
                *, 
                default_cluster_resource_placement: Optional[ClusterResourcePlacementSpec] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.PlacementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PICK_ALL = "PickAll"
        PICK_FIXED = "PickFixed"


    class azure.mgmt.containerservicefleet.models.PolicyRule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_ALL = "AllowAll"
        ALLOW_SAME_NAMESPACE = "AllowSameNamespace"
        DENY_ALL = "DenyAll"


    class azure.mgmt.containerservicefleet.models.PropagationPolicy(_Model):
        placement_profile: Optional[PlacementProfile]
        type: Union[str, PropagationType]

        @overload
        def __init__(
                self, 
                *, 
                placement_profile: Optional[PlacementProfile] = ..., 
                type: Union[str, PropagationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.PropagationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLACEMENT = "Placement"


    class azure.mgmt.containerservicefleet.models.PropertySelector(_Model):
        match_expressions: list[PropertySelectorRequirement]

        @overload
        def __init__(
                self, 
                *, 
                match_expressions: list[PropertySelectorRequirement]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.PropertySelectorOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQ = "Eq"
        GE = "Ge"
        GT = "Gt"
        LE = "Le"
        LT = "Lt"
        NE = "Ne"


    class azure.mgmt.containerservicefleet.models.PropertySelectorRequirement(_Model):
        name: str
        operator: Union[str, PropertySelectorOperator]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operator: Union[str, PropertySelectorOperator], 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerservicefleet.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerservicefleet.models.ResourceQuota(_Model):
        cpu_limit: Optional[str]
        cpu_request: Optional[str]
        memory_limit: Optional[str]
        memory_request: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cpu_limit: Optional[str] = ..., 
                cpu_request: Optional[str] = ..., 
                memory_limit: Optional[str] = ..., 
                memory_request: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.SkipProperties(_Model):
        targets: list[SkipTarget]

        @overload
        def __init__(
                self, 
                *, 
                targets: list[SkipTarget]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.SkipTarget(_Model):
        name: str
        type: Union[str, TargetType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, TargetType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.SystemData(_Model):
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


    class azure.mgmt.containerservicefleet.models.TaintEffect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_SCHEDULE = "NoSchedule"


    class azure.mgmt.containerservicefleet.models.TargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFTER_STAGE_WAIT = "AfterStageWait"
        GROUP = "Group"
        MEMBER = "Member"
        STAGE = "Stage"


    class azure.mgmt.containerservicefleet.models.Timing(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFTER = "After"
        BEFORE = "Before"


    class azure.mgmt.containerservicefleet.models.Toleration(_Model):
        effect: Optional[Union[str, TaintEffect]]
        key: Optional[str]
        operator: Optional[Union[str, TolerationOperator]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                effect: Optional[Union[str, TaintEffect]] = ..., 
                key: Optional[str] = ..., 
                operator: Optional[Union[str, TolerationOperator]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.TolerationOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"
        EXISTS = "Exists"


    class azure.mgmt.containerservicefleet.models.TrackedResource(Resource):
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


    class azure.mgmt.containerservicefleet.models.UpdateGroup(_Model):
        after_gates: Optional[list[GateConfiguration]]
        before_gates: Optional[list[GateConfiguration]]
        max_concurrency: Optional[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                after_gates: Optional[list[GateConfiguration]] = ..., 
                before_gates: Optional[list[GateConfiguration]] = ..., 
                max_concurrency: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.UpdateGroupStatus(_Model):
        after_gates: Optional[list[UpdateRunGateStatus]]
        before_gates: Optional[list[UpdateRunGateStatus]]
        max_concurrency: Optional[int]
        members: Optional[list[MemberUpdateStatus]]
        name: Optional[str]
        status: Optional[UpdateStatus]


    class azure.mgmt.containerservicefleet.models.UpdateRun(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[UpdateRunProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.containerservicefleet.models.UpdateRunGateStatus(_Model):
        display_name: Optional[str]
        gate_id: Optional[str]
        status: Optional[UpdateStatus]


    class azure.mgmt.containerservicefleet.models.UpdateRunGateTargetProperties(_Model):
        group: Optional[str]
        name: str
        stage: Optional[str]
        timing: Union[str, Timing]

        @overload
        def __init__(
                self, 
                *, 
                timing: Union[str, Timing]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.UpdateRunProperties(_Model):
        auto_upgrade_profile_id: Optional[str]
        managed_cluster_update: ManagedClusterUpdate
        provisioning_state: Optional[Union[str, UpdateRunProvisioningState]]
        status: Optional[UpdateRunStatus]
        strategy: Optional[UpdateRunStrategy]
        update_strategy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                managed_cluster_update: ManagedClusterUpdate, 
                strategy: Optional[UpdateRunStrategy] = ..., 
                update_strategy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.UpdateRunProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerservicefleet.models.UpdateRunStatus(_Model):
        node_image_selection: Optional[NodeImageSelectionStatus]
        stages: Optional[list[UpdateStageStatus]]
        status: Optional[UpdateStatus]


    class azure.mgmt.containerservicefleet.models.UpdateRunStrategy(_Model):
        stages: list[UpdateStage]

        @overload
        def __init__(
                self, 
                *, 
                stages: list[UpdateStage]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.UpdateStage(_Model):
        after_gates: Optional[list[GateConfiguration]]
        after_stage_wait_in_seconds: Optional[int]
        before_gates: Optional[list[GateConfiguration]]
        groups: Optional[list[UpdateGroup]]
        max_concurrency: Optional[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                after_gates: Optional[list[GateConfiguration]] = ..., 
                after_stage_wait_in_seconds: Optional[int] = ..., 
                before_gates: Optional[list[GateConfiguration]] = ..., 
                groups: Optional[list[UpdateGroup]] = ..., 
                max_concurrency: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerservicefleet.models.UpdateStageStatus(_Model):
        after_gates: Optional[list[UpdateRunGateStatus]]
        after_stage_wait_status: Optional[WaitStatus]
        before_gates: Optional[list[UpdateRunGateStatus]]
        groups: Optional[list[UpdateGroupStatus]]
        max_concurrency: Optional[int]
        name: Optional[str]
        status: Optional[UpdateStatus]


    class azure.mgmt.containerservicefleet.models.UpdateState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        PENDING = "Pending"
        RUNNING = "Running"
        SKIPPED = "Skipped"
        STOPPED = "Stopped"
        STOPPING = "Stopping"


    class azure.mgmt.containerservicefleet.models.UpdateStatus(_Model):
        completed_time: Optional[datetime]
        error: Optional[ErrorDetail]
        start_time: Optional[datetime]
        state: Optional[Union[str, UpdateState]]


    class azure.mgmt.containerservicefleet.models.UpgradeChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NODE_IMAGE = "NodeImage"
        RAPID = "Rapid"
        STABLE = "Stable"
        TARGET_KUBERNETES_VERSION = "TargetKubernetesVersion"


    class azure.mgmt.containerservicefleet.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.containerservicefleet.models.WaitStatus(_Model):
        status: Optional[UpdateStatus]
        wait_duration_in_seconds: Optional[int]


namespace azure.mgmt.containerservicefleet.operations

    class azure.mgmt.containerservicefleet.operations.AutoUpgradeProfileOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-01', params_added_on={'2025-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'accept']}, api_versions_list=['2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def begin_generate_update_run(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[GenerateResponse]: ...


    class azure.mgmt.containerservicefleet.operations.AutoUpgradeProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                resource: AutoUpgradeProfile, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AutoUpgradeProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AutoUpgradeProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AutoUpgradeProfile]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-02-preview', params_added_on={'2024-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'etag', 'match_condition']}, api_versions_list=['2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-02-preview', params_added_on={'2024-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'accept']}, api_versions_list=['2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                auto_upgrade_profile_name: str, 
                **kwargs: Any
            ) -> AutoUpgradeProfile: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-05-02-preview', params_added_on={'2024-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'top', 'skip_token', 'accept']}, api_versions_list=['2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AutoUpgradeProfile]: ...


    class azure.mgmt.containerservicefleet.operations.FleetManagedNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                resource: FleetManagedNamespace, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetManagedNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetManagedNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetManagedNamespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01-preview', params_added_on={'2025-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'managed_namespace_name', 'etag', 'match_condition']}, api_versions_list=['2025-08-01-preview', '2026-02-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                properties: FleetManagedNamespacePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetManagedNamespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetManagedNamespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetManagedNamespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01-preview', params_added_on={'2025-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'managed_namespace_name', 'accept']}, api_versions_list=['2025-08-01-preview', '2026-02-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                managed_namespace_name: str, 
                **kwargs: Any
            ) -> FleetManagedNamespace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01-preview', params_added_on={'2025-08-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'accept']}, api_versions_list=['2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FleetManagedNamespace]: ...


    class azure.mgmt.containerservicefleet.operations.FleetMembersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                resource: FleetMember, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetMember]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetMember]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetMember]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                properties: FleetMemberUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetMember]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetMember]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetMember]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                fleet_member_name: str, 
                **kwargs: Any
            ) -> FleetMember: ...

        @distributed_trace
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FleetMember]: ...


    class azure.mgmt.containerservicefleet.operations.FleetUpdateStrategiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                resource: FleetUpdateStrategy, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetUpdateStrategy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetUpdateStrategy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[FleetUpdateStrategy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-08-15-preview', params_added_on={'2023-08-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_strategy_name', 'etag', 'match_condition']}, api_versions_list=['2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-08-15-preview', params_added_on={'2023-08-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_strategy_name', 'accept']}, api_versions_list=['2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_strategy_name: str, 
                **kwargs: Any
            ) -> FleetUpdateStrategy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-08-15-preview', params_added_on={'2023-08-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'top', 'skip_token', 'accept']}, api_versions_list=['2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[FleetUpdateStrategy]: ...


    class azure.mgmt.containerservicefleet.operations.FleetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: Fleet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: FleetPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> Fleet: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Fleet]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Fleet]: ...

        @distributed_trace
        def list_credentials(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> FleetCredentialResults: ...


    class azure.mgmt.containerservicefleet.operations.GatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                properties: GatePatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Gate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Gate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[Gate]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'gate_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                gate_name: str, 
                **kwargs: Any
            ) -> Gate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'filter', 'top', 'skip_token', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Gate]: ...


    class azure.mgmt.containerservicefleet.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.containerservicefleet.operations.UpdateRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                resource: UpdateRun, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'etag', 'match_condition']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_skip(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                body: SkipProperties, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @overload
        def begin_skip(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @overload
        def begin_skip(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'accept', 'etag', 'match_condition']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def begin_start(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'accept', 'etag', 'match_condition']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def begin_stop(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateRun]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'update_run_name', 'accept']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                update_run_name: str, 
                **kwargs: Any
            ) -> UpdateRun: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-03-15-preview', params_added_on={'2023-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name', 'top', 'skip_token', 'accept']}, api_versions_list=['2023-03-15-preview', '2023-06-15-preview', '2023-08-15-preview', '2023-10-15', '2024-02-02-preview', '2024-04-01', '2024-05-02-preview', '2025-03-01', '2025-04-01-preview', '2025-08-01-preview', '2026-02-01-preview'])
        def list_by_fleet(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[UpdateRun]: ...


```