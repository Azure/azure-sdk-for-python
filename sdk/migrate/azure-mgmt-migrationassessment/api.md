```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.migrationassessment

    class azure.mgmt.migrationassessment.MigrationAssessmentMgmtClient: implements ContextManager 
        assessed_machines_operations: AssessedMachinesOperationsOperations
        assessed_sql_database_v2_operations: AssessedSqlDatabaseV2OperationsOperations
        assessed_sql_instance_v2_operations: AssessedSqlInstanceV2OperationsOperations
        assessed_sql_machines_operations: AssessedSqlMachinesOperationsOperations
        assessed_sql_recommended_entity_operations: AssessedSqlRecommendedEntityOperationsOperations
        assessment_options_operations: AssessmentOptionsOperationsOperations
        assessment_project_summary_operations: AssessmentProjectSummaryOperationsOperations
        assessment_projects_operations: AssessmentProjectsOperationsOperations
        assessments_operations: AssessmentsOperationsOperations
        avs_assessed_machines_operations: AvsAssessedMachinesOperationsOperations
        avs_assessment_options_operations: AvsAssessmentOptionsOperationsOperations
        avs_assessments_operations: AvsAssessmentsOperationsOperations
        groups_operations: GroupsOperationsOperations
        hyperv_collectors_operations: HypervCollectorsOperationsOperations
        import_collectors_operations: ImportCollectorsOperationsOperations
        machines_operations: MachinesOperationsOperations
        operations: Operations
        private_endpoint_connection_operations: PrivateEndpointConnectionOperationsOperations
        private_link_resource_operations: PrivateLinkResourceOperationsOperations
        server_collectors_operations: ServerCollectorsOperationsOperations
        sql_assessment_options_operations: SqlAssessmentOptionsOperationsOperations
        sql_assessment_v2_operations: SqlAssessmentV2OperationsOperations
        sql_assessment_v2_summary_operations: SqlAssessmentV2SummaryOperationsOperations
        sql_collector_operations: SqlCollectorOperationsOperations
        vmware_collectors_operations: VmwareCollectorsOperationsOperations

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


namespace azure.mgmt.migrationassessment.aio

    class azure.mgmt.migrationassessment.aio.MigrationAssessmentMgmtClient: implements AsyncContextManager 
        assessed_machines_operations: AssessedMachinesOperationsOperations
        assessed_sql_database_v2_operations: AssessedSqlDatabaseV2OperationsOperations
        assessed_sql_instance_v2_operations: AssessedSqlInstanceV2OperationsOperations
        assessed_sql_machines_operations: AssessedSqlMachinesOperationsOperations
        assessed_sql_recommended_entity_operations: AssessedSqlRecommendedEntityOperationsOperations
        assessment_options_operations: AssessmentOptionsOperationsOperations
        assessment_project_summary_operations: AssessmentProjectSummaryOperationsOperations
        assessment_projects_operations: AssessmentProjectsOperationsOperations
        assessments_operations: AssessmentsOperationsOperations
        avs_assessed_machines_operations: AvsAssessedMachinesOperationsOperations
        avs_assessment_options_operations: AvsAssessmentOptionsOperationsOperations
        avs_assessments_operations: AvsAssessmentsOperationsOperations
        groups_operations: GroupsOperationsOperations
        hyperv_collectors_operations: HypervCollectorsOperationsOperations
        import_collectors_operations: ImportCollectorsOperationsOperations
        machines_operations: MachinesOperationsOperations
        operations: Operations
        private_endpoint_connection_operations: PrivateEndpointConnectionOperationsOperations
        private_link_resource_operations: PrivateLinkResourceOperationsOperations
        server_collectors_operations: ServerCollectorsOperationsOperations
        sql_assessment_options_operations: SqlAssessmentOptionsOperationsOperations
        sql_assessment_v2_operations: SqlAssessmentV2OperationsOperations
        sql_assessment_v2_summary_operations: SqlAssessmentV2SummaryOperationsOperations
        sql_collector_operations: SqlCollectorOperationsOperations
        vmware_collectors_operations: VmwareCollectorsOperationsOperations

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


namespace azure.mgmt.migrationassessment.aio.operations

    class azure.mgmt.migrationassessment.aio.operations.AssessedMachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_machine_name: str, 
                **kwargs: Any
            ) -> AssessedMachine: ...

        @distributed_trace
        def list_by_assessment(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AssessedMachine]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessedSqlDatabaseV2OperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_sql_database_name: str, 
                **kwargs: Any
            ) -> AssessedSqlDatabaseV2: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AssessedSqlDatabaseV2]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessedSqlInstanceV2OperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_sql_instance_name: str, 
                **kwargs: Any
            ) -> AssessedSqlInstanceV2: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AssessedSqlInstanceV2]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessedSqlMachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_sql_machine_name: str, 
                **kwargs: Any
            ) -> AssessedSqlMachine: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AssessedSqlMachine]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessedSqlRecommendedEntityOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                recommended_assessed_entity_name: str, 
                **kwargs: Any
            ) -> AssessedSqlRecommendedEntity: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AssessedSqlRecommendedEntity]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessmentOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_options_name: str, 
                **kwargs: Any
            ) -> AssessmentOptions: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AssessmentOptions]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessmentProjectSummaryOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                project_summary_name: str, 
                **kwargs: Any
            ) -> AssessmentProjectSummary: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AssessmentProjectSummary]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessmentProjectsOperationsOperations:

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
                resource: AssessmentProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssessmentProject]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssessmentProject]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                properties: AssessmentProjectUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssessmentProject]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssessmentProject]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AssessmentProject: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AssessmentProject]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[AssessmentProject]: ...


    class azure.mgmt.migrationassessment.aio.operations.AssessmentsOperationsOperations:

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
                group_name: str, 
                assessment_name: str, 
                resource: Assessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Assessment]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Assessment]: ...

        @distributed_trace_async
        async def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> AsyncLROPoller[DownloadUrl]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> Assessment: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Assessment]: ...


    class azure.mgmt.migrationassessment.aio.operations.AvsAssessedMachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                avs_assessed_machine_name: str, 
                **kwargs: Any
            ) -> AvsAssessedMachine: ...

        @distributed_trace
        def list_by_avs_assessment(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AvsAssessedMachine]: ...


    class azure.mgmt.migrationassessment.aio.operations.AvsAssessmentOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                avs_assessment_options_name: str, 
                **kwargs: Any
            ) -> AvsAssessmentOptions: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AvsAssessmentOptions]: ...


    class azure.mgmt.migrationassessment.aio.operations.AvsAssessmentsOperationsOperations:

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
                group_name: str, 
                assessment_name: str, 
                resource: AvsAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsAssessment]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvsAssessment]: ...

        @distributed_trace_async
        async def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> AsyncLROPoller[DownloadUrl]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AvsAssessment: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AvsAssessment]: ...


    class azure.mgmt.migrationassessment.aio.operations.GroupsOperationsOperations:

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
                group_name: str, 
                resource: Group, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Group]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Group]: ...

        @overload
        async def begin_update_machines(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                body: UpdateGroupBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Group]: ...

        @overload
        async def begin_update_machines(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Group]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> Group: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Group]: ...


    class azure.mgmt.migrationassessment.aio.operations.HypervCollectorsOperationsOperations:

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
                hyperv_collector_name: str, 
                resource: HypervCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HypervCollector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                hyperv_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HypervCollector]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                hyperv_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                hyperv_collector_name: str, 
                **kwargs: Any
            ) -> HypervCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[HypervCollector]: ...


    class azure.mgmt.migrationassessment.aio.operations.ImportCollectorsOperationsOperations:

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
                import_collector_name: str, 
                resource: ImportCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportCollector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                import_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportCollector]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                import_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                import_collector_name: str, 
                **kwargs: Any
            ) -> ImportCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ImportCollector]: ...


    class azure.mgmt.migrationassessment.aio.operations.MachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Machine]: ...


    class azure.mgmt.migrationassessment.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.migrationassessment.aio.operations.PrivateEndpointConnectionOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnection]: ...


    class azure.mgmt.migrationassessment.aio.operations.PrivateLinkResourceOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


    class azure.mgmt.migrationassessment.aio.operations.ServerCollectorsOperationsOperations:

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
                server_collector_name: str, 
                resource: ServerCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerCollector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                server_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServerCollector]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                server_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                server_collector_name: str, 
                **kwargs: Any
            ) -> ServerCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ServerCollector]: ...


    class azure.mgmt.migrationassessment.aio.operations.SqlAssessmentOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_options_name: str, 
                **kwargs: Any
            ) -> SqlAssessmentOptions: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SqlAssessmentOptions]: ...


    class azure.mgmt.migrationassessment.aio.operations.SqlAssessmentV2OperationsOperations:

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
                group_name: str, 
                assessment_name: str, 
                resource: SqlAssessmentV2, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlAssessmentV2]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlAssessmentV2]: ...

        @distributed_trace_async
        async def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> AsyncLROPoller[DownloadUrl]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> SqlAssessmentV2: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SqlAssessmentV2]: ...


    class azure.mgmt.migrationassessment.aio.operations.SqlAssessmentV2SummaryOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                summary_name: str, 
                **kwargs: Any
            ) -> SqlAssessmentV2Summary: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SqlAssessmentV2Summary]: ...


    class azure.mgmt.migrationassessment.aio.operations.SqlCollectorOperationsOperations:

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
                collector_name: str, 
                resource: SqlCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlCollector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlCollector]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                collector_name: str, 
                **kwargs: Any
            ) -> SqlCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SqlCollector]: ...


    class azure.mgmt.migrationassessment.aio.operations.VmwareCollectorsOperationsOperations:

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
                vm_ware_collector_name: str, 
                resource: VmwareCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmwareCollector]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                vm_ware_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VmwareCollector]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                vm_ware_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                vm_ware_collector_name: str, 
                **kwargs: Any
            ) -> VmwareCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[VmwareCollector]: ...


namespace azure.mgmt.migrationassessment.models

    class azure.mgmt.migrationassessment.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.migrationassessment.models.ApiVersions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2019_10_01 = "2019-10-01"
        V2020_01_01 = "2020-01-01"
        V2020_05_01_PREVIEW = "2020-05-01-preview"
        V2022_02_02_PREVIEW = "2022-02-02-preview"
        V2023_03_03 = "2023-03-03"
        V2023_03_15 = "2023-03-15"
        V2023_04_01_PREVIEW = "2023-04-01-preview"
        V2023_07_07_PREVIEW = "2023-07-07-preview"


    class azure.mgmt.migrationassessment.models.AssessedDisk(Model):
        display_name: str
        gigabytes_for_recommended_disk_size: int
        gigabytes_provisioned: float
        megabytes_per_second_of_read: float
        megabytes_per_second_of_write: float
        monthly_storage_cost: float
        name: str
        number_of_read_operations_per_second: float
        number_of_write_operations_per_second: float
        recommend_disk_throughput_in_mbps: float
        recommended_disk_iops: float
        recommended_disk_size: Union[str, AzureDiskSize]
        recommended_disk_type: Union[str, AzureDiskType]
        suitability: Union[str, CloudSuitability]
        suitability_detail: Union[str, AzureDiskSuitabilityDetail]
        suitability_explanation: Union[str, AzureDiskSuitabilityExplanation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                gigabytes_for_recommended_disk_size: Optional[int] = ..., 
                gigabytes_provisioned: Optional[float] = ..., 
                megabytes_per_second_of_read: Optional[float] = ..., 
                megabytes_per_second_of_write: Optional[float] = ..., 
                monthly_storage_cost: Optional[float] = ..., 
                name: Optional[str] = ..., 
                number_of_read_operations_per_second: Optional[float] = ..., 
                number_of_write_operations_per_second: Optional[float] = ..., 
                recommend_disk_throughput_in_mbps: Optional[float] = ..., 
                recommended_disk_iops: Optional[float] = ..., 
                recommended_disk_size: Optional[Union[str, AzureDiskSize]] = ..., 
                recommended_disk_type: Optional[Union[str, AzureDiskType]] = ..., 
                suitability: Optional[Union[str, CloudSuitability]] = ..., 
                suitability_detail: Optional[Union[str, AzureDiskSuitabilityDetail]] = ..., 
                suitability_explanation: Optional[Union[str, AzureDiskSuitabilityExplanation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedDiskData(Model):
        display_name: str
        gigabytes_provisioned: float
        megabytes_per_second_of_read: float
        megabytes_per_second_of_write: float
        monthly_storage_cost: float
        name: str
        number_of_read_operations_per_second: float
        number_of_write_operations_per_second: float
        recommend_disk_throughput_in_mbps: float
        recommended_disk_iops: float
        recommended_disk_size: Union[str, AzureDiskSize]
        recommended_disk_size_gigabytes: int
        recommended_disk_type: Union[str, AzureDiskType]
        suitability: Union[str, CloudSuitability]
        suitability_detail: Union[str, AzureDiskSuitabilityDetail]
        suitability_explanation: Union[str, AzureDiskSuitabilityExplanation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                gigabytes_provisioned: Optional[float] = ..., 
                megabytes_per_second_of_read: Optional[float] = ..., 
                megabytes_per_second_of_write: Optional[float] = ..., 
                monthly_storage_cost: Optional[float] = ..., 
                name: Optional[str] = ..., 
                number_of_read_operations_per_second: Optional[float] = ..., 
                number_of_write_operations_per_second: Optional[float] = ..., 
                recommend_disk_throughput_in_mbps: Optional[float] = ..., 
                recommended_disk_iops: Optional[float] = ..., 
                recommended_disk_size: Optional[Union[str, AzureDiskSize]] = ..., 
                recommended_disk_size_gigabytes: Optional[int] = ..., 
                recommended_disk_type: Optional[Union[str, AzureDiskType]] = ..., 
                suitability: Optional[Union[str, CloudSuitability]] = ..., 
                suitability_detail: Optional[Union[str, AzureDiskSuitabilityDetail]] = ..., 
                suitability_explanation: Optional[Union[str, AzureDiskSuitabilityExplanation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedMachine(ProxyResource):
        id: str
        name: str
        properties: AssessedMachineProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessedMachineProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedMachineListResult(Model):
        next_link: str
        value: list[AssessedMachine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessedMachine], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedMachineProperties(Model):
        boot_type: Union[str, MachineBootType]
        confidence_rating_in_percentage: float
        cost_components: list[CostComponent]
        created_timestamp: datetime
        datacenter_machine_arm_id: str
        datacenter_management_server_arm_id: str
        datacenter_management_server_name: str
        description: str
        disks: dict[str, AssessedDisk]
        display_name: str
        errors: list[Error]
        host_processor: ProcessorInfo
        megabytes_of_memory: float
        megabytes_of_memory_for_recommended_size: float
        monthly_bandwidth_cost: float
        monthly_compute_cost_for_recommended_size: float
        monthly_premium_storage_cost: float
        monthly_standard_ssd_storage_cost: float
        monthly_storage_cost: float
        monthly_ultra_storage_cost: float
        network_adapters: dict[str, AssessedNetworkAdapter]
        number_of_cores: int
        number_of_cores_for_recommended_size: int
        operating_system_architecture: Union[str, GuestOperatingSystemArchitecture]
        operating_system_name: str
        operating_system_type: str
        operating_system_version: str
        percentage_cores_utilization: float
        percentage_memory_utilization: float
        product_support_status: ProductSupportStatus
        recommended_size: Union[str, AzureVmSize]
        suitability: Union[str, CloudSuitability]
        suitability_detail: Union[str, AzureVmSuitabilityDetail]
        suitability_explanation: Union[str, AzureVmSuitabilityExplanation]
        type: Union[str, AssessedMachineType]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_components: Optional[List[CostComponent]] = ..., 
                host_processor: Optional[ProcessorInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedMachineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSESSED_MACHINE = "AssessedMachine"
        AVS_ASSESSED_MACHINE = "AvsAssessedMachine"
        SQL_ASSESSED_MACHINE = "SqlAssessedMachine"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AssessedNetworkAdapter(Model):
        display_name: str
        ip_addresses: list[str]
        mac_address: str
        megabytes_per_second_received: float
        megabytes_per_second_transmitted: float
        monthly_bandwidth_costs: float
        net_gigabytes_transmitted_per_month: float
        suitability: Union[str, CloudSuitability]
        suitability_detail: Union[str, AzureNetworkAdapterSuitabilityDetail]
        suitability_explanation: Union[str, AzureNetworkAdapterSuitabilityExplanation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                mac_address: Optional[str] = ..., 
                megabytes_per_second_received: Optional[float] = ..., 
                megabytes_per_second_transmitted: Optional[float] = ..., 
                monthly_bandwidth_costs: Optional[float] = ..., 
                net_gigabytes_transmitted_per_month: Optional[float] = ..., 
                suitability: Optional[Union[str, CloudSuitability]] = ..., 
                suitability_detail: Optional[Union[str, AzureNetworkAdapterSuitabilityDetail]] = ..., 
                suitability_explanation: Optional[Union[str, AzureNetworkAdapterSuitabilityExplanation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlDatabaseV2(ProxyResource):
        id: str
        name: str
        properties: AssessedSqlDatabaseV2Properties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessedSqlDatabaseV2Properties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlDatabaseV2ListResult(Model):
        next_link: str
        value: list[AssessedSqlDatabaseV2]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessedSqlDatabaseV2], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlDatabaseV2Properties(Model):
        assessed_sql_instance_arm_id: str
        azure_sql_db_suitability_details: SqlAssessmentV2PaasSuitabilityData
        azure_sql_mi_suitability_details: SqlAssessmentV2PaasSuitabilityData
        buffer_cache_size_in_mb: float
        compatibility_level: Union[str, CompatibilityLevel]
        confidence_rating_in_percentage: float
        created_timestamp: datetime
        database_name: str
        database_size_in_mb: float
        instance_name: str
        is_database_highly_available: bool
        linked_availability_group_overview: SqlAvailabilityGroupDataOverview
        machine_arm_id: str
        machine_name: str
        megabytes_per_second_of_read: float
        megabytes_per_second_of_write: float
        number_of_read_operations_per_second: float
        number_of_write_operations_per_second: float
        percentage_cores_utilization: float
        product_support_status: ProductSupportStatus
        recommended_azure_sql_target_type: Union[str, TargetType]
        recommended_suitability: Union[str, RecommendedSuitability]
        sizing_criterion: Union[str, AssessmentSizingCriterion]
        sql_database_sds_arm_id: str
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlInstanceDatabaseSummary(Model):
        largest_database_size_in_mb: float
        number_of_user_databases: int
        total_database_size_in_mb: float
        total_discovered_user_databases: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                largest_database_size_in_mb: Optional[float] = ..., 
                number_of_user_databases: Optional[int] = ..., 
                total_database_size_in_mb: Optional[float] = ..., 
                total_discovered_user_databases: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlInstanceDiskDetails(Model):
        disk_id: str
        disk_size_in_mb: float
        megabytes_per_second_of_read: float
        megabytes_per_second_of_write: float
        number_of_read_operations_per_second: float
        number_of_write_operations_per_second: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_id: Optional[str] = ..., 
                disk_size_in_mb: Optional[float] = ..., 
                megabytes_per_second_of_read: Optional[float] = ..., 
                megabytes_per_second_of_write: Optional[float] = ..., 
                number_of_read_operations_per_second: Optional[float] = ..., 
                number_of_write_operations_per_second: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlInstanceStorageDetails(Model):
        disk_size_in_mb: float
        megabytes_per_second_of_read: float
        megabytes_per_second_of_write: float
        number_of_read_operations_per_second: float
        number_of_write_operations_per_second: float
        storage_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_size_in_mb: Optional[float] = ..., 
                megabytes_per_second_of_read: Optional[float] = ..., 
                megabytes_per_second_of_write: Optional[float] = ..., 
                number_of_read_operations_per_second: Optional[float] = ..., 
                number_of_write_operations_per_second: Optional[float] = ..., 
                storage_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlInstanceSummary(Model):
        instance_id: str
        instance_name: str
        is_clustered: bool
        is_high_availability_enabled: bool
        sql_edition: str
        sql_fci_state: Union[str, SqlFCIState]
        sql_instance_entity_id: str
        sql_instance_sds_arm_id: str
        sql_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_id: Optional[str] = ..., 
                instance_name: Optional[str] = ..., 
                is_clustered: Optional[bool] = ..., 
                is_high_availability_enabled: Optional[bool] = ..., 
                sql_edition: Optional[str] = ..., 
                sql_fci_state: Optional[Union[str, SqlFCIState]] = ..., 
                sql_instance_entity_id: Optional[str] = ..., 
                sql_instance_sds_arm_id: Optional[str] = ..., 
                sql_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlInstanceV2(ProxyResource):
        id: str
        name: str
        properties: AssessedSqlInstanceV2Properties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessedSqlInstanceV2Properties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlInstanceV2ListResult(Model):
        next_link: str
        value: list[AssessedSqlInstanceV2]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessedSqlInstanceV2], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlInstanceV2Properties(Model):
        availability_replica_summary: SqlAvailabilityReplicaSummary
        azure_sql_db_suitability_details: SqlAssessmentV2PaasSuitabilityData
        azure_sql_mi_suitability_details: SqlAssessmentV2PaasSuitabilityData
        azure_sql_vm_suitability_details: SqlAssessmentV2IaasSuitabilityData
        confidence_rating_in_percentage: float
        created_timestamp: datetime
        database_summary: AssessedSqlInstanceDatabaseSummary
        fci_metadata: SqlFCIMetadata
        has_scan_occurred: bool
        instance_name: str
        is_clustered: bool
        is_high_availability_enabled: bool
        logical_disks: list[AssessedSqlInstanceDiskDetails]
        machine_arm_id: str
        machine_name: str
        memory_in_use_in_mb: float
        number_of_cores_allocated: int
        percentage_cores_utilization: float
        product_support_status: ProductSupportStatus
        recommended_azure_sql_target_type: Union[str, TargetType]
        recommended_suitability: Union[str, RecommendedSuitability]
        recommended_target_reasonings: list[SqlRecommendationReasoning]
        sizing_criterion: Union[str, AssessmentSizingCriterion]
        sql_edition: str
        sql_instance_sds_arm_id: str
        sql_version: str
        storage_type_based_details: list[AssessedSqlInstanceStorageDetails]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlMachine(ProxyResource):
        id: str
        name: str
        properties: AssessedSqlMachineProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessedSqlMachineProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlMachineListResult(Model):
        next_link: str
        value: list[AssessedSqlMachine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessedSqlMachine], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlMachineProperties(Model):
        bios_guid: str
        boot_type: Union[str, MachineBootType]
        confidence_rating_in_percentage: float
        cost_components: list[CostComponent]
        created_timestamp: datetime
        datacenter_machine_arm_id: str
        datacenter_management_server_arm_id: str
        datacenter_management_server_name: str
        description: str
        disks: dict[str, AssessedDiskData]
        display_name: str
        fqdn: str
        megabytes_of_memory: float
        migration_guidelines: list[SqlMigrationGuideline]
        monthly_bandwidth_cost: float
        monthly_compute_cost: float
        monthly_storage_cost: float
        network_adapters: dict[str, SqlAssessedNetworkAdapter]
        number_of_cores: int
        operating_system_architecture: Union[str, GuestOperatingSystemArchitecture]
        operating_system_name: str
        operating_system_type: str
        operating_system_version: str
        percentage_cores_utilization: float
        percentage_memory_utilization: float
        product_support_status: ProductSupportStatus
        recommended_vm_family: Union[str, AzureVmFamily]
        recommended_vm_size: Union[str, AzureVmSize]
        recommended_vm_size_megabytes_of_memory: float
        recommended_vm_size_number_of_cores: int
        security_suitability: Union[str, CloudSuitability]
        sizing_criterion: Union[str, AssessmentSizingCriterion]
        sql_instances: list[AssessedSqlInstanceSummary]
        suitability: Union[str, CloudSuitability]
        suitability_detail: Union[str, AzureVmSuitabilityDetail]
        suitability_explanation: Union[str, AzureVmSuitabilityExplanation]
        type: Union[str, AssessedMachineType]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_components: Optional[List[CostComponent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlRecommendedEntity(ProxyResource):
        id: str
        name: str
        properties: AssessedSqlRecommendedEntityProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessedSqlRecommendedEntityProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlRecommendedEntityListResult(Model):
        next_link: str
        value: list[AssessedSqlRecommendedEntity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessedSqlRecommendedEntity], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessedSqlRecommendedEntityProperties(Model):
        assessed_sql_entity_arm_id: str
        azure_sql_db_suitability_details: SqlAssessmentV2PaasSuitabilityData
        azure_sql_mi_suitability_details: SqlAssessmentV2PaasSuitabilityData
        azure_sql_vm_suitability_details: SqlAssessmentV2IaasSuitabilityData
        db_count: int
        discovered_db_count: int
        has_scan_occurred: bool
        instance_name: str
        is_clustered: bool
        is_high_availability_enabled: bool
        machine_name: str
        product_support_status: ProductSupportStatus
        recommended_azure_sql_target_type: Union[str, TargetType]
        recommended_suitability: Union[str, RecommendedSuitability]
        sizing_criterion: Union[str, AssessmentSizingCriterion]
        sql_edition: str
        sql_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessed_sql_entity_arm_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.Assessment(ProxyResource):
        id: str
        name: str
        properties: MachineAssessmentProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MachineAssessmentProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentListResult(Model):
        next_link: str
        value: list[Assessment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Assessment], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentOptions(ProxyResource):
        id: str
        name: str
        properties: AssessmentOptionsProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessmentOptionsProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentOptionsListResult(Model):
        next_link: str
        value: list[AssessmentOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessmentOptions], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentOptionsProperties(Model):
        premium_disk_vm_families: list[str]
        reserved_instance_supported_currencies: list[str]
        reserved_instance_supported_locations: list[str]
        reserved_instance_supported_offers: list[str]
        reserved_instance_vm_families: list[str]
        savings_plan_supported_locations: list[str]
        savings_plan_vm_families: list[str]
        ultra_disk_vm_families: list[UltraDiskAssessmentOptions]
        vm_families: list[VmFamilyOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentProject(TrackedResource):
        id: str
        location: str
        name: str
        properties: ProjectProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ProjectProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentProjectListResult(Model):
        next_link: str
        value: list[AssessmentProject]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessmentProject], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentProjectSummary(ProxyResource):
        id: str
        name: str
        properties: AssessmentProjectSummaryProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessmentProjectSummaryProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentProjectSummaryListResult(Model):
        next_link: str
        value: list[AssessmentProjectSummary]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AssessmentProjectSummary], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentProjectSummaryProperties(Model):
        error_summary_affected_entities: list[ErrorSummary]
        last_assessment_timestamp: datetime
        number_of_assessments: int
        number_of_groups: int
        number_of_import_machines: int
        number_of_machines: int
        number_of_private_endpoint_connections: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentProjectUpdate(Model):
        properties: AssessmentProjectUpdateProperties
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssessmentProjectUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentProjectUpdateProperties(Model):
        assessment_solution_id: str
        customer_storage_account_arm_id: str
        customer_workspace_id: str
        customer_workspace_location: str
        project_status: Union[str, ProjectStatus]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_solution_id: Optional[str] = ..., 
                customer_storage_account_arm_id: Optional[str] = ..., 
                customer_workspace_id: Optional[str] = ..., 
                customer_workspace_location: Optional[str] = ..., 
                project_status: Optional[Union[str, ProjectStatus]] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                public_network_access: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AssessmentSizingCriterion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AS_ON_PREMISES = "AsOnPremises"
        PERFORMANCE_BASED = "PerformanceBased"


    class azure.mgmt.migrationassessment.models.AssessmentStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        IN_PROGRESS = "InProgress"
        UNDER_REVIEW = "UnderReview"


    class azure.mgmt.migrationassessment.models.AssessmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        CREATED = "Created"
        DELETED = "Deleted"
        INVALID = "Invalid"
        OUT_DATED = "OutDated"
        OUT_OF_SYNC = "OutOfSync"
        RUNNING = "Running"
        UPDATED = "Updated"


    class azure.mgmt.migrationassessment.models.AssessmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVS_ASSESSMENT = "AvsAssessment"
        MACHINE_ASSESSMENT = "MachineAssessment"
        SQL_ASSESSMENT = "SqlAssessment"
        UNKNOWN = "Unknown"
        WEB_APP_ASSESSMENT = "WebAppAssessment"


    class azure.mgmt.migrationassessment.models.AsyncCommitModeIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISASTER_RECOVERY = "DisasterRecovery"
        HIGH_AVAILABILITY = "HighAvailability"
        NONE = "None"


    class azure.mgmt.migrationassessment.models.AvsAssessedDisk(Model):
        display_name: str
        gigabytes_provisioned: float
        megabytes_per_second_of_read: float
        megabytes_per_second_of_write: float
        name: str
        number_of_read_operations_per_second: float
        number_of_write_operations_per_second: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessedMachine(ProxyResource):
        id: str
        name: str
        properties: AvsAssessedMachineProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AvsAssessedMachineProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessedMachineListResult(Model):
        next_link: str
        value: list[AvsAssessedMachine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AvsAssessedMachine], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessedMachineProperties(Model):
        boot_type: Union[str, MachineBootType]
        confidence_rating_in_percentage: float
        created_timestamp: datetime
        datacenter_machine_arm_id: str
        datacenter_management_server_arm_id: str
        datacenter_management_server_name: str
        description: str
        disks: dict[str, AvsAssessedDisk]
        display_name: str
        errors: list[Error]
        megabytes_of_memory: float
        network_adapters: dict[str, AvsAssessedNetworkAdapter]
        number_of_cores: int
        operating_system_architecture: Union[str, GuestOperatingSystemArchitecture]
        operating_system_name: str
        operating_system_type: str
        operating_system_version: str
        percentage_cores_utilization: float
        percentage_memory_utilization: float
        storage_in_use_gb: float
        suitability: Union[str, CloudSuitability]
        suitability_detail: Union[str, AzureAvsVmSuitabilityDetail]
        suitability_explanation: Union[str, AzureAvsVmSuitabilityExplanation]
        type: Union[str, AssessedMachineType]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessedNetworkAdapter(Model):
        display_name: str
        ip_addresses: list[str]
        mac_address: str
        megabytes_per_second_received: float
        megabytes_per_second_transmitted: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessment(ProxyResource):
        id: str
        name: str
        properties: AvsAssessmentProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AvsAssessmentProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessmentListResult(Model):
        next_link: str
        value: list[AvsAssessment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AvsAssessment], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessmentOptions(ProxyResource):
        id: str
        name: str
        properties: AvsAssessmentOptionsProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AvsAssessmentOptionsProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessmentOptionsListResult(Model):
        next_link: str
        value: list[AvsAssessmentOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[AvsAssessmentOptions], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessmentOptionsProperties(Model):
        avs_nodes: list[AvsSkuOptions]
        failures_to_tolerate_and_raid_level_values: Union[list[str, FttAndRaidLevel]]
        reserved_instance_avs_nodes: Union[list[str, AzureAvsNodeType]]
        reserved_instance_supported_currencies: Union[list[str, AzureCurrency]]
        reserved_instance_supported_locations: Union[list[str, AzureLocation]]
        reserved_instance_supported_offers: Union[list[str, AzureOfferCode]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                avs_nodes: Optional[List[AvsSkuOptions]] = ..., 
                failures_to_tolerate_and_raid_level_values: Optional[List[Union[str, FttAndRaidLevel]]] = ..., 
                reserved_instance_avs_nodes: Optional[List[Union[str, AzureAvsNodeType]]] = ..., 
                reserved_instance_supported_currencies: Optional[List[Union[str, AzureCurrency]]] = ..., 
                reserved_instance_supported_locations: Optional[List[Union[str, AzureLocation]]] = ..., 
                reserved_instance_supported_offers: Optional[List[Union[str, AzureOfferCode]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsAssessmentProperties(AzureResourceProperties):
        assessment_error_summary: dict[str, int]
        assessment_type: Union[str, AssessmentType]
        azure_location: Union[str, AzureLocation]
        azure_offer_code: Union[str, AzureOfferCode]
        confidence_rating_in_percentage: float
        cpu_utilization: float
        created_timestamp: datetime
        currency: Union[str, AzureCurrency]
        dedupe_compression: float
        discount_percentage: float
        failures_to_tolerate_and_raid_level: Union[str, FttAndRaidLevel]
        group_type: Union[str, GroupType]
        is_stretch_cluster_enabled: bool
        limiting_factor: str
        mem_overcommit: float
        node_type: Union[str, AzureAvsNodeType]
        number_of_machines: int
        number_of_nodes: int
        percentile: Union[str, Percentile]
        perf_data_end_time: datetime
        perf_data_start_time: datetime
        prices_timestamp: datetime
        provisioning_state: Union[str, ProvisioningState]
        ram_utilization: float
        reserved_instance: Union[str, AzureReservedInstance]
        scaling_factor: float
        schema_version: str
        sizing_criterion: Union[str, AssessmentSizingCriterion]
        stage: Union[str, AssessmentStage]
        status: Union[str, AssessmentStatus]
        storage_utilization: float
        suitability: Union[str, CloudSuitability]
        suitability_explanation: Union[str, AzureAvsSuitabilityExplanation]
        suitability_summary: dict[str, int]
        time_range: Union[str, TimeRange]
        total_cpu_cores: float
        total_monthly_cost: float
        total_ram_in_gb: float
        total_storage_in_gb: float
        updated_timestamp: datetime
        vcpu_oversubscription: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_location: Optional[Union[str, AzureLocation]] = ..., 
                azure_offer_code: Optional[Union[str, AzureOfferCode]] = ..., 
                currency: Optional[Union[str, AzureCurrency]] = ..., 
                dedupe_compression: Optional[float] = ..., 
                discount_percentage: Optional[float] = ..., 
                failures_to_tolerate_and_raid_level: Optional[Union[str, FttAndRaidLevel]] = ..., 
                is_stretch_cluster_enabled: Optional[bool] = ..., 
                mem_overcommit: Optional[float] = ..., 
                node_type: Optional[Union[str, AzureAvsNodeType]] = ..., 
                percentile: Optional[Union[str, Percentile]] = ..., 
                perf_data_end_time: Optional[datetime] = ..., 
                perf_data_start_time: Optional[datetime] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                reserved_instance: Optional[Union[str, AzureReservedInstance]] = ..., 
                scaling_factor: Optional[float] = ..., 
                sizing_criterion: Optional[Union[str, AssessmentSizingCriterion]] = ..., 
                time_range: Optional[Union[str, TimeRange]] = ..., 
                vcpu_oversubscription: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AvsSkuOptions(Model):
        node_type: Union[str, AzureAvsNodeType]
        target_locations: Union[list[str, AzureLocation]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                node_type: Optional[Union[str, AzureAvsNodeType]] = ..., 
                target_locations: Optional[List[Union[str, AzureLocation]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AzureAvsNodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AV36 = "AV36"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureAvsSuitabilityExplanation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "NotApplicable"
        UNKNOWN = "Unknown"
        UNSUPPORTED_LOCATION_FOR_SELECTED_NODE = "UnsupportedLocationForSelectedNode"


    class azure.mgmt.migrationassessment.models.AzureAvsVmSuitabilityDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        PERCENTAGE_OF_CORES_UTILIZED_MISSING = "PercentageOfCoresUtilizedMissing"
        PERCENTAGE_OF_CORES_UTILIZED_OUT_OF_RANGE = "PercentageOfCoresUtilizedOutOfRange"
        PERCENTAGE_OF_MEMORY_UTILIZED_MISSING = "PercentageOfMemoryUtilizedMissing"
        PERCENTAGE_OF_MEMORY_UTILIZED_OUT_OF_RANGE = "PercentageOfMemoryUtilizedOutOfRange"
        PERCENTAGE_OF_STORAGE_UTILIZED_OUT_OF_RANGE = "PercentageOfStorageUtilizedOutOfRange"


    class azure.mgmt.migrationassessment.models.AzureAvsVmSuitabilityExplanation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IP_V6_NOT_SUPPORTED = "IpV6NotSupported"
        NOT_APPLICABLE = "NotApplicable"
        UNKNOWN = "Unknown"
        UNSUPPORTED_OPERATING_SYSTEM = "UnsupportedOperatingSystem"


    class azure.mgmt.migrationassessment.models.AzureCurrency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARS = "ARS"
        AUD = "AUD"
        BRL = "BRL"
        CAD = "CAD"
        CHF = "CHF"
        CNY = "CNY"
        DKK = "DKK"
        EUR = "EUR"
        GBP = "GBP"
        HKD = "HKD"
        IDR = "IDR"
        INR = "INR"
        JPY = "JPY"
        KRW = "KRW"
        MXN = "MXN"
        MYR = "MYR"
        NOK = "NOK"
        NZD = "NZD"
        RUB = "RUB"
        SAR = "SAR"
        SEK = "SEK"
        TRY = "TRY"
        TRY_ENUM = "TRY"
        TWD = "TWD"
        UNKNOWN = "Unknown"
        USD = "USD"
        ZAR = "ZAR"


    class azure.mgmt.migrationassessment.models.AzureDiskSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_P1 = "Premium_P1"
        PREMIUM_P10 = "Premium_P10"
        PREMIUM_P15 = "Premium_P15"
        PREMIUM_P2 = "Premium_P2"
        PREMIUM_P20 = "Premium_P20"
        PREMIUM_P3 = "Premium_P3"
        PREMIUM_P30 = "Premium_P30"
        PREMIUM_P4 = "Premium_P4"
        PREMIUM_P40 = "Premium_P40"
        PREMIUM_P50 = "Premium_P50"
        PREMIUM_P6 = "Premium_P6"
        PREMIUM_P60 = "Premium_P60"
        PREMIUM_P70 = "Premium_P70"
        PREMIUM_P80 = "Premium_P80"
        PREMIUM_V2 = "PremiumV2"
        STANDARD_S10 = "Standard_S10"
        STANDARD_S15 = "Standard_S15"
        STANDARD_S20 = "Standard_S20"
        STANDARD_S30 = "Standard_S30"
        STANDARD_S4 = "Standard_S4"
        STANDARD_S40 = "Standard_S40"
        STANDARD_S50 = "Standard_S50"
        STANDARD_S6 = "Standard_S6"
        STANDARD_S60 = "Standard_S60"
        STANDARD_S70 = "Standard_S70"
        STANDARD_S80 = "Standard_S80"
        STANDARD_SSDE1 = "StandardSSD_E1"
        STANDARD_SSDE10 = "StandardSSD_E10"
        STANDARD_SSDE15 = "StandardSSD_E15"
        STANDARD_SSDE2 = "StandardSSD_E2"
        STANDARD_SSDE20 = "StandardSSD_E20"
        STANDARD_SSDE3 = "StandardSSD_E3"
        STANDARD_SSDE30 = "StandardSSD_E30"
        STANDARD_SSDE4 = "StandardSSD_E4"
        STANDARD_SSDE40 = "StandardSSD_E40"
        STANDARD_SSDE50 = "StandardSSD_E50"
        STANDARD_SSDE6 = "StandardSSD_E6"
        STANDARD_SSDE60 = "StandardSSD_E60"
        STANDARD_SSDE70 = "StandardSSD_E70"
        STANDARD_SSDE80 = "StandardSSD_E80"
        ULTRA = "Ultra"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureDiskSuitabilityDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_GIGABYTES_CONSUMED_MISSING = "DiskGigabytesConsumedMissing"
        DISK_GIGABYTES_CONSUMED_OUT_OF_RANGE = "DiskGigabytesConsumedOutOfRange"
        DISK_GIGABYTES_PROVISIONED_MISSING = "DiskGigabytesProvisionedMissing"
        DISK_GIGABYTES_PROVISIONED_OUT_OF_RANGE = "DiskGigabytesProvisionedOutOfRange"
        MEGABYTES_PER_SECOND_OF_READ_MISSING = "MegabytesPerSecondOfReadMissing"
        MEGABYTES_PER_SECOND_OF_READ_OUT_OF_RANGE = "MegabytesPerSecondOfReadOutOfRange"
        MEGABYTES_PER_SECOND_OF_WRITE_MISSING = "MegabytesPerSecondOfWriteMissing"
        MEGABYTES_PER_SECOND_OF_WRITE_OUT_OF_RANGE = "MegabytesPerSecondOfWriteOutOfRange"
        NONE = "None"
        NUMBER_OF_READ_OPERATIONS_PER_SECOND_MISSING = "NumberOfReadOperationsPerSecondMissing"
        NUMBER_OF_READ_OPERATIONS_PER_SECOND_OUT_OF_RANGE = "NumberOfReadOperationsPerSecondOutOfRange"
        NUMBER_OF_WRITE_OPERATIONS_PER_SECOND_MISSING = "NumberOfWriteOperationsPerSecondMissing"
        NUMBER_OF_WRITE_OPERATIONS_PER_SECOND_OUT_OF_RANGE = "NumberOfWriteOperationsPerSecondOutOfRange"


    class azure.mgmt.migrationassessment.models.AzureDiskSuitabilityExplanation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_SIZE_GREATER_THAN_SUPPORTED = "DiskSizeGreaterThanSupported"
        INTERNAL_ERROR_OCCURRED_FOR_DISK_EVALUATION = "InternalErrorOccurredForDiskEvaluation"
        NOT_APPLICABLE = "NotApplicable"
        NO_DISK_SIZE_FOUND_FOR_SELECTED_REDUNDANCY = "NoDiskSizeFoundForSelectedRedundancy"
        NO_DISK_SIZE_FOUND_IN_SELECTED_LOCATION = "NoDiskSizeFoundInSelectedLocation"
        NO_EA_PRICE_FOUND_FOR_DISK_SIZE = "NoEaPriceFoundForDiskSize"
        NO_SUITABLE_DISK_SIZE_FOR_IOPS = "NoSuitableDiskSizeForIops"
        NO_SUITABLE_DISK_SIZE_FOR_THROUGHPUT = "NoSuitableDiskSizeForThroughput"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureDiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        PREMIUM_V2 = "PremiumV2"
        STANDARD = "Standard"
        STANDARD_OR_PREMIUM = "StandardOrPremium"
        STANDARD_SSD = "StandardSSD"
        ULTRA = "Ultra"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureHybridUseBenefit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        UNKNOWN = "Unknown"
        YES = "Yes"


    class azure.mgmt.migrationassessment.models.AzureLocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUSTRALIA_CENTRAL = "AustraliaCentral"
        AUSTRALIA_CENTRAL2 = "AustraliaCentral2"
        AUSTRALIA_EAST = "AustraliaEast"
        AUSTRALIA_SOUTHEAST = "AustraliaSoutheast"
        BRAZIL_SOUTH = "BrazilSouth"
        CANADA_CENTRAL = "CanadaCentral"
        CANADA_EAST = "CanadaEast"
        CENTRAL_INDIA = "CentralIndia"
        CENTRAL_US = "CentralUs"
        CHINA_EAST = "ChinaEast"
        CHINA_EAST2 = "ChinaEast2"
        CHINA_NORTH = "ChinaNorth"
        CHINA_NORTH2 = "ChinaNorth2"
        EAST_ASIA = "EastAsia"
        EAST_US = "EastUs"
        EAST_US2 = "EastUs2"
        FRANCE_CENTRAL = "FranceCentral"
        FRANCE_SOUTH = "FranceSouth"
        GERMANY_CENTRAL = "GermanyCentral"
        GERMANY_NORTH = "GermanyNorth"
        GERMANY_NORTHEAST = "GermanyNortheast"
        GERMANY_WEST_CENTRAL = "GermanyWestCentral"
        JAPAN_EAST = "JapanEast"
        JAPAN_WEST = "JapanWest"
        KOREA_CENTRAL = "KoreaCentral"
        KOREA_SOUTH = "KoreaSouth"
        NORTH_CENTRAL_US = "NorthCentralUs"
        NORTH_EUROPE = "NorthEurope"
        NORWAY_EAST = "NorwayEast"
        NORWAY_WEST = "NorwayWest"
        QATAR_CENTRAL = "QatarCentral"
        SOUTHEAST_ASIA = "SoutheastAsia"
        SOUTH_AFRICA_NORTH = "SouthAfricaNorth"
        SOUTH_AFRICA_WEST = "SouthAfricaWest"
        SOUTH_CENTRAL_US = "SouthCentralUs"
        SOUTH_INDIA = "SouthIndia"
        SWEDEN_CENTRAL = "SwedenCentral"
        SWITZERLAND_NORTH = "SwitzerlandNorth"
        SWITZERLAND_WEST = "SwitzerlandWest"
        UAE_CENTRAL = "UAECentral"
        UAE_NORTH = "UAENorth"
        UK_SOUTH = "UkSouth"
        UK_WEST = "UkWest"
        UNKNOWN = "Unknown"
        US_DO_D_CENTRAL = "USDoDCentral"
        US_DO_D_EAST = "USDoDEast"
        US_GOV_ARIZONA = "USGovArizona"
        US_GOV_IOWA = "USGovIowa"
        US_GOV_TEXAS = "USGovTexas"
        US_GOV_VIRGINIA = "USGovVirginia"
        US_NAT_EAST = "UsNatEast"
        US_NAT_WEST = "UsNatWest"
        US_SEC_CENTRAL = "UsSecCentral"
        US_SEC_EAST = "UsSecEast"
        US_SEC_WEST = "UsSecWest"
        WEST_CENTRAL_US = "WestCentralUs"
        WEST_EUROPE = "WestEurope"
        WEST_INDIA = "WestIndia"
        WEST_US = "WestUs"
        WEST_US2 = "WestUs2"


    class azure.mgmt.migrationassessment.models.AzureManagedDiskSkuDTO(Model):
        disk_redundancy: Union[str, AzureManagedDiskSkuDTODiskRedundancy]
        disk_size: Union[str, AzureDiskSize]
        disk_type: Union[str, AzureManagedDiskSkuDTODiskType]
        recommended_iops: float
        recommended_size_in_gib: float
        recommended_throughput_in_mbps: float
        storage_cost: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AzureManagedDiskSkuDTODiskRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LRS = "LRS"
        UNKNOWN = "Unknown"
        ZRS = "ZRS"


    class azure.mgmt.migrationassessment.models.AzureManagedDiskSkuDTODiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        PREMIUM_V2 = "PremiumV2"
        STANDARD = "Standard"
        STANDARD_OR_PREMIUM = "StandardOrPremium"
        STANDARD_SSD = "StandardSSD"
        ULTRA = "Ultra"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureNetworkAdapterSuitabilityDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEGABYTES_OF_DATA_RECIEVED_MISSING = "MegabytesOfDataRecievedMissing"
        MEGABYTES_OF_DATA_RECIEVED_OUT_OF_RANGE = "MegabytesOfDataRecievedOutOfRange"
        MEGABYTES_OF_DATA_TRANSMITTED_MISSING = "MegabytesOfDataTransmittedMissing"
        MEGABYTES_OF_DATA_TRANSMITTED_OUT_OF_RANGE = "MegabytesOfDataTransmittedOutOfRange"
        NONE = "None"


    class azure.mgmt.migrationassessment.models.AzureNetworkAdapterSuitabilityExplanation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL_ERROR_OCCURRED = "InternalErrorOccurred"
        NOT_APPLICABLE = "NotApplicable"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureOfferCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EA = "EA"
        MSAZR0003_P = "MSAZR0003P"
        MSAZR0022_P = "MSAZR0022P"
        MSAZR0023_P = "MSAZR0023P"
        MSAZR0025_P = "MSAZR0025P"
        MSAZR0029_P = "MSAZR0029P"
        MSAZR0036_P = "MSAZR0036P"
        MSAZR0044_P = "MSAZR0044P"
        MSAZR0059_P = "MSAZR0059P"
        MSAZR0060_P = "MSAZR0060P"
        MSAZR0062_P = "MSAZR0062P"
        MSAZR0063_P = "MSAZR0063P"
        MSAZR0064_P = "MSAZR0064P"
        MSAZR0111_P = "MSAZR0111P"
        MSAZR0120_P = "MSAZR0120P"
        MSAZR0121_P = "MSAZR0121P"
        MSAZR0122_P = "MSAZR0122P"
        MSAZR0123_P = "MSAZR0123P"
        MSAZR0124_P = "MSAZR0124P"
        MSAZR0125_P = "MSAZR0125P"
        MSAZR0126_P = "MSAZR0126P"
        MSAZR0127_P = "MSAZR0127P"
        MSAZR0128_P = "MSAZR0128P"
        MSAZR0129_P = "MSAZR0129P"
        MSAZR0130_P = "MSAZR0130P"
        MSAZR0144_P = "MSAZR0144P"
        MSAZR0148_P = "MSAZR0148P"
        MSAZR0149_P = "MSAZR0149P"
        MSAZR0243_P = "MSAZR0243P"
        MSAZRDE0003_P = "MSAZRDE0003P"
        MSAZRDE0044_P = "MSAZRDE0044P"
        MSAZRUSGOV0003_P = "MSAZRUSGOV0003P"
        MSMCAZR0044_P = "MSMCAZR0044P"
        MSMCAZR0059_P = "MSMCAZR0059P"
        MSMCAZR0060_P = "MSMCAZR0060P"
        MSMCAZR0063_P = "MSMCAZR0063P"
        MSMCAZR0120_P = "MSMCAZR0120P"
        MSMCAZR0121_P = "MSMCAZR0121P"
        MSMCAZR0125_P = "MSMCAZR0125P"
        MSMCAZR0128_P = "MSMCAZR0128P"
        SAVINGS_PLAN1_YEAR = "SavingsPlan1Year"
        SAVINGS_PLAN3_YEAR = "SavingsPlan3Year"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzurePricingTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.migrationassessment.models.AzureQuorumWitnessDTO(Model):
        quorum_witness_type: Union[str, AzureQuorumWitnessDTOQuorumWitnessType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AzureQuorumWitnessDTOQuorumWitnessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD = "Cloud"
        DISK = "Disk"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureReservedInstance(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        RI1_YEAR = "RI1Year"
        RI3_YEAR = "RI3Year"


    class azure.mgmt.migrationassessment.models.AzureResourceProperties(Model):
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AzureSecurityOfferingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MDC = "MDC"
        NO = "NO"


    class azure.mgmt.migrationassessment.models.AzureSqlDataBaseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        ELASTIC_POOL = "ElasticPool"
        SINGLE_DATABASE = "SingleDatabase"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureSqlIaasSkuDTO(Model):
        azure_sql_target_type: Union[str, TargetType]
        data_disk_sizes: list[AzureManagedDiskSkuDTO]
        log_disk_sizes: list[AzureManagedDiskSkuDTO]
        virtual_machine_size: AzureVirtualMachineSkuDTO

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AzureSqlInstanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        INSTANCE_POOLS = "InstancePools"
        SINGLE_INSTANCE = "SingleInstance"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureSqlPaasSkuDTO(Model):
        azure_sql_compute_tier: Union[str, ComputeTier]
        azure_sql_hardware_generation: Union[str, HardwareGeneration]
        azure_sql_service_tier: Union[str, AzureSqlServiceTier]
        azure_sql_target_type: Union[str, TargetType]
        cores: int
        predicted_data_size_in_mb: float
        predicted_log_size_in_mb: float
        storage_max_size_in_mb: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AzureSqlPurchaseModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DTU = "DTU"
        UNKNOWN = "Unknown"
        V_CORE = "VCore"


    class azure.mgmt.migrationassessment.models.AzureSqlServiceTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        BUSINESS_CRITICAL = "BusinessCritical"
        GENERAL_PURPOSE = "GeneralPurpose"
        HYPER_SCALE = "HyperScale"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureStorageRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_REDUNDANT = "GeoRedundant"
        LOCALLY_REDUNDANT = "LocallyRedundant"
        READ_ACCESS_GEO_REDUNDANT = "ReadAccessGeoRedundant"
        UNKNOWN = "Unknown"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.migrationassessment.models.AzureVirtualMachineSkuDTO(Model):
        available_cores: int
        azure_sku_name: Union[str, AzureVmSize]
        azure_vm_family: Union[str, AzureVmFamily]
        cores: int
        max_network_interfaces: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.AzureVmFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AV2_SERIES = "Av2_series"
        BASIC_A0_A4 = "Basic_A0_A4"
        DADSV5_SERIES = "Dadsv5_series"
        DASV4_SERIES = "Dasv4_series"
        DASV5_SERIES = "Dasv5_series"
        DAV4_SERIES = "Dav4_series"
        DC_SERIES = "DC_Series"
        DDSV4_SERIES = "Ddsv4_series"
        DDSV5_SERIES = "Ddsv5_series"
        DDV4_SERIES = "Ddv4_series"
        DDV5_SERIES = "Ddv5_series"
        DSV3_SERIES = "Dsv3_series"
        DSV4_SERIES = "Dsv4_series"
        DSV5_SERIES = "Dsv5_series"
        DS_SERIES = "DS_series"
        DV2_SERIES = "Dv2_series"
        DV3_SERIES = "Dv3_series"
        DV4_SERIES = "Dv4_series"
        DV5_SERIES = "Dv5_series"
        D_SERIES = "D_series"
        D_SV2_SERIES = "DSv2_series"
        EADSV5_SERIES = "Eadsv5_series"
        EASV4_SERIES = "Easv4_series"
        EASV5_SERIES = "Easv5_series"
        EAV4_SERIES = "Eav4_series"
        EBDSV5_SERIES = "Ebdsv5_series"
        EBSV5_SERIES = "Ebsv5_series"
        EDSV4_SERIES = "Edsv4_series"
        EDSV5_SERIES = "Edsv5_series"
        EDV4_SERIES = "Edv4_series"
        EDV5_SERIES = "Edv5_series"
        ESV3_SERIES = "Esv3_series"
        ESV4_SERIES = "Esv4_series"
        ESV5_SERIES = "Esv5_series"
        EV3_SERIES = "Ev3_series"
        EV4_SERIES = "Ev4_series"
        EV5_SERIES = "Ev5_series"
        FSV2_SERIES = "Fsv2_series"
        FS_SERIES = "Fs_series"
        F_SERIES = "F_series"
        GS_SERIES = "GS_series"
        G_SERIES = "G_series"
        H_SERIES = "H_series"
        LSV2_SERIES = "Lsv2_series"
        LS_SERIES = "Ls_series"
        MDSV2_SERIES = "Mdsv2_series"
        MSV2_SERIES = "Msv2_series"
        MV2_SERIES = "Mv2_series"
        M_SERIES = "M_series"
        STANDARD_A0_A7 = "Standard_A0_A7"
        STANDARD_A8_A11 = "Standard_A8_A11"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureVmSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC_A0 = "Basic_A0"
        BASIC_A1 = "Basic_A1"
        BASIC_A2 = "Basic_A2"
        BASIC_A3 = "Basic_A3"
        BASIC_A4 = "Basic_A4"
        STANDARD_A0 = "Standard_A0"
        STANDARD_A1 = "Standard_A1"
        STANDARD_A10 = "Standard_A10"
        STANDARD_A11 = "Standard_A11"
        STANDARD_A1_V2 = "Standard_A1_v2"
        STANDARD_A2 = "Standard_A2"
        STANDARD_A2_MV2 = "Standard_A2m_v2"
        STANDARD_A2_V2 = "Standard_A2_v2"
        STANDARD_A3 = "Standard_A3"
        STANDARD_A4 = "Standard_A4"
        STANDARD_A4_MV2 = "Standard_A4m_v2"
        STANDARD_A4_V2 = "Standard_A4_v2"
        STANDARD_A5 = "Standard_A5"
        STANDARD_A6 = "Standard_A6"
        STANDARD_A7 = "Standard_A7"
        STANDARD_A8 = "Standard_A8"
        STANDARD_A8_MV2 = "Standard_A8m_v2"
        STANDARD_A8_V2 = "Standard_A8_v2"
        STANDARD_A9 = "Standard_A9"
        STANDARD_D1 = "Standard_D1"
        STANDARD_D11 = "Standard_D11"
        STANDARD_D11_V2 = "Standard_D11_v2"
        STANDARD_D12 = "Standard_D12"
        STANDARD_D12_V2 = "Standard_D12_v2"
        STANDARD_D13 = "Standard_D13"
        STANDARD_D13_V2 = "Standard_D13_v2"
        STANDARD_D14 = "Standard_D14"
        STANDARD_D14_V2 = "Standard_D14_v2"
        STANDARD_D15_V2 = "Standard_D15_v2"
        STANDARD_D16_ADS_V5 = "Standard_D16ads_v5"
        STANDARD_D16_AS_V4 = "Standard_D16as_v4"
        STANDARD_D16_AS_V5 = "Standard_D16as_v5"
        STANDARD_D16_AV4 = "Standard_D16a_v4"
        STANDARD_D16_DS_V4 = "Standard_D16ds_v4"
        STANDARD_D16_DS_V5 = "Standard_D16ds_v5"
        STANDARD_D16_DV4 = "Standard_D16d_v4"
        STANDARD_D16_DV5 = "Standard_D16d_v5"
        STANDARD_D16_SV3 = "Standard_D16s_v3"
        STANDARD_D16_SV4 = "Standard_D16s_v4"
        STANDARD_D16_SV5 = "Standard_D16s_v5"
        STANDARD_D16_V3 = "Standard_D16_v3"
        STANDARD_D16_V4 = "Standard_D16_v4"
        STANDARD_D16_V5 = "Standard_D16_v5"
        STANDARD_D1_V2 = "Standard_D1_v2"
        STANDARD_D2 = "Standard_D2"
        STANDARD_D2_ADS_V5 = "Standard_D2ads_v5"
        STANDARD_D2_AS_V4 = "Standard_D2as_v4"
        STANDARD_D2_AS_V5 = "Standard_D2as_v5"
        STANDARD_D2_AV4 = "Standard_D2a_v4"
        STANDARD_D2_DS_V4 = "Standard_D2ds_v4"
        STANDARD_D2_DS_V5 = "Standard_D2ds_v5"
        STANDARD_D2_DV4 = "Standard_D2d_v4"
        STANDARD_D2_DV5 = "Standard_D2d_v5"
        STANDARD_D2_SV3 = "Standard_D2s_v3"
        STANDARD_D2_SV4 = "Standard_D2s_v4"
        STANDARD_D2_SV5 = "Standard_D2s_v5"
        STANDARD_D2_V2 = "Standard_D2_v2"
        STANDARD_D2_V3 = "Standard_D2_v3"
        STANDARD_D2_V4 = "Standard_D2_v4"
        STANDARD_D2_V5 = "Standard_D2_v5"
        STANDARD_D3 = "Standard_D3"
        STANDARD_D32_ADS_V5 = "Standard_D32ads_v5"
        STANDARD_D32_AS_V4 = "Standard_D32as_v4"
        STANDARD_D32_AS_V5 = "Standard_D32as_v5"
        STANDARD_D32_AV4 = "Standard_D32a_v4"
        STANDARD_D32_DS_V4 = "Standard_D32ds_v4"
        STANDARD_D32_DS_V5 = "Standard_D32ds_v5"
        STANDARD_D32_DV4 = "Standard_D32d_v4"
        STANDARD_D32_DV5 = "Standard_D32d_v5"
        STANDARD_D32_SV3 = "Standard_D32s_v3"
        STANDARD_D32_SV4 = "Standard_D32s_v4"
        STANDARD_D32_SV5 = "Standard_D32s_v5"
        STANDARD_D32_V3 = "Standard_D32_v3"
        STANDARD_D32_V4 = "Standard_D32_v4"
        STANDARD_D32_V5 = "Standard_D32_v5"
        STANDARD_D3_V2 = "Standard_D3_v2"
        STANDARD_D4 = "Standard_D4"
        STANDARD_D48_ADS_V5 = "Standard_D48ads_v5"
        STANDARD_D48_AS_V4 = "Standard_D48as_v4"
        STANDARD_D48_AS_V5 = "Standard_D48as_v5"
        STANDARD_D48_AV4 = "Standard_D48a_v4"
        STANDARD_D48_DS_V4 = "Standard_D48ds_v4"
        STANDARD_D48_DS_V5 = "Standard_D48ds_v5"
        STANDARD_D48_DV4 = "Standard_D48d_v4"
        STANDARD_D48_DV5 = "Standard_D48d_v5"
        STANDARD_D48_SV4 = "Standard_D48s_v4"
        STANDARD_D48_SV5 = "Standard_D48s_v5"
        STANDARD_D48_V4 = "Standard_D48_v4"
        STANDARD_D48_V5 = "Standard_D48_v5"
        STANDARD_D4_ADS_V5 = "Standard_D4ads_v5"
        STANDARD_D4_AS_V4 = "Standard_D4as_v4"
        STANDARD_D4_AS_V5 = "Standard_D4as_v5"
        STANDARD_D4_AV4 = "Standard_D4a_v4"
        STANDARD_D4_DS_V4 = "Standard_D4ds_v4"
        STANDARD_D4_DS_V5 = "Standard_D4ds_v5"
        STANDARD_D4_DV4 = "Standard_D4d_v4"
        STANDARD_D4_DV5 = "Standard_D4d_v5"
        STANDARD_D4_SV3 = "Standard_D4s_v3"
        STANDARD_D4_SV4 = "Standard_D4s_v4"
        STANDARD_D4_SV5 = "Standard_D4s_v5"
        STANDARD_D4_V2 = "Standard_D4_v2"
        STANDARD_D4_V3 = "Standard_D4_v3"
        STANDARD_D4_V4 = "Standard_D4_v4"
        STANDARD_D4_V5 = "Standard_D4_v5"
        STANDARD_D5_V2 = "Standard_D5_v2"
        STANDARD_D64_ADS_V5 = "Standard_D64ads_v5"
        STANDARD_D64_AS_V4 = "Standard_D64as_v4"
        STANDARD_D64_AS_V5 = "Standard_D64as_v5"
        STANDARD_D64_AV4 = "Standard_D64a_v4"
        STANDARD_D64_DS_V4 = "Standard_D64ds_v4"
        STANDARD_D64_DS_V5 = "Standard_D64ds_v5"
        STANDARD_D64_DV4 = "Standard_D64d_v4"
        STANDARD_D64_DV5 = "Standard_D64d_v5"
        STANDARD_D64_SV3 = "Standard_D64s_v3"
        STANDARD_D64_SV4 = "Standard_D64s_v4"
        STANDARD_D64_SV5 = "Standard_D64s_v5"
        STANDARD_D64_V3 = "Standard_D64_v3"
        STANDARD_D64_V4 = "Standard_D64_v4"
        STANDARD_D64_V5 = "Standard_D64_v5"
        STANDARD_D8_ADS_V5 = "Standard_D8ads_v5"
        STANDARD_D8_AS_V4 = "Standard_D8as_v4"
        STANDARD_D8_AS_V5 = "Standard_D8as_v5"
        STANDARD_D8_AV4 = "Standard_D8a_v4"
        STANDARD_D8_DS_V4 = "Standard_D8ds_v4"
        STANDARD_D8_DS_V5 = "Standard_D8ds_v5"
        STANDARD_D8_DV4 = "Standard_D8d_v4"
        STANDARD_D8_DV5 = "Standard_D8d_v5"
        STANDARD_D8_SV3 = "Standard_D8s_v3"
        STANDARD_D8_SV4 = "Standard_D8s_v4"
        STANDARD_D8_SV5 = "Standard_D8s_v5"
        STANDARD_D8_V3 = "Standard_D8_v3"
        STANDARD_D8_V4 = "Standard_D8_v4"
        STANDARD_D8_V5 = "Standard_D8_v5"
        STANDARD_D96_ADS_V5 = "Standard_D96ads_v5"
        STANDARD_D96_AS_V4 = "Standard_D96as_v4"
        STANDARD_D96_AS_V5 = "Standard_D96as_v5"
        STANDARD_D96_AV4 = "Standard_D96a_v4"
        STANDARD_D96_DS_V5 = "Standard_D96ds_v5"
        STANDARD_D96_DV5 = "Standard_D96d_v5"
        STANDARD_D96_SV5 = "Standard_D96s_v5"
        STANDARD_D96_V5 = "Standard_D96_v5"
        STANDARD_DC2_S = "Standard_DC2s"
        STANDARD_DC4_S = "Standard_DC4s"
        STANDARD_DS1 = "Standard_DS1"
        STANDARD_DS11 = "Standard_DS11"
        STANDARD_DS111_V2 = "Standard_DS11_1_v2"
        STANDARD_DS11_V2 = "Standard_DS11_v2"
        STANDARD_DS12 = "Standard_DS12"
        STANDARD_DS121_V2 = "Standard_DS12_1_v2"
        STANDARD_DS122_V2 = "Standard_DS12_2_v2"
        STANDARD_DS12_V2 = "Standard_DS12_v2"
        STANDARD_DS13 = "Standard_DS13"
        STANDARD_DS132_V2 = "Standard_DS13_2_v2"
        STANDARD_DS134_V2 = "Standard_DS13_4_v2"
        STANDARD_DS13_V2 = "Standard_DS13_v2"
        STANDARD_DS14 = "Standard_DS14"
        STANDARD_DS144_V2 = "Standard_DS14_4_v2"
        STANDARD_DS148_V2 = "Standard_DS14_8_v2"
        STANDARD_DS14_V2 = "Standard_DS14_v2"
        STANDARD_DS15_V2 = "Standard_DS15_v2"
        STANDARD_DS1_V2 = "Standard_DS1_v2"
        STANDARD_DS2 = "Standard_DS2"
        STANDARD_DS2_V2 = "Standard_DS2_v2"
        STANDARD_DS3 = "Standard_DS3"
        STANDARD_DS3_V2 = "Standard_DS3_v2"
        STANDARD_DS4 = "Standard_DS4"
        STANDARD_DS4_V2 = "Standard_DS4_v2"
        STANDARD_DS5_V2 = "Standard_DS5_v2"
        STANDARD_E104_IDS_V5 = "Standard_E104ids_v5"
        STANDARD_E104_ID_V5 = "Standard_E104id_v5"
        STANDARD_E104_IS_V5 = "Standard_E104is_v5"
        STANDARD_E104_IV5 = "Standard_E104i_v5"
        STANDARD_E164_ADS_V5 = "Standard_E16_4ads_v5"
        STANDARD_E164_AS_V4 = "Standard_E16_4as_v4"
        STANDARD_E164_AS_V5 = "Standard_E16_4as_v5"
        STANDARD_E164_DS_V4 = "Standard_E16_4ds_v4"
        STANDARD_E164_DS_V5 = "Standard_E16_4ds_v5"
        STANDARD_E164_SV3 = "Standard_E16_4s_v3"
        STANDARD_E164_SV4 = "Standard_E16_4s_v4"
        STANDARD_E164_SV5 = "Standard_E16_4s_v5"
        STANDARD_E168_ADS_V5 = "Standard_E16_8ads_v5"
        STANDARD_E168_AS_V4 = "Standard_E16_8as_v4"
        STANDARD_E168_AS_V5 = "Standard_E16_8as_v5"
        STANDARD_E168_DS_V4 = "Standard_E16_8ds_v4"
        STANDARD_E168_DS_V5 = "Standard_E16_8ds_v5"
        STANDARD_E168_SV3 = "Standard_E16_8s_v3"
        STANDARD_E168_SV4 = "Standard_E16_8s_v4"
        STANDARD_E168_SV5 = "Standard_E16_8s_v5"
        STANDARD_E16_ADS_V5 = "Standard_E16ads_v5"
        STANDARD_E16_AS_V4 = "Standard_E16as_v4"
        STANDARD_E16_AS_V5 = "Standard_E16as_v5"
        STANDARD_E16_AV4 = "Standard_E16a_v4"
        STANDARD_E16_BDS_V5 = "Standard_E16bds_v5"
        STANDARD_E16_BS_V5 = "Standard_E16bs_v5"
        STANDARD_E16_DS_V4 = "Standard_E16ds_v4"
        STANDARD_E16_DS_V5 = "Standard_E16ds_v5"
        STANDARD_E16_DV4 = "Standard_E16d_v4"
        STANDARD_E16_DV5 = "Standard_E16d_v5"
        STANDARD_E16_SV3 = "Standard_E16s_v3"
        STANDARD_E16_SV4 = "Standard_E16s_v4"
        STANDARD_E16_SV5 = "Standard_E16s_v5"
        STANDARD_E16_V3 = "Standard_E16_v3"
        STANDARD_E16_V4 = "Standard_E16_v4"
        STANDARD_E16_V5 = "Standard_E16_v5"
        STANDARD_E20_ADS_V5 = "Standard_E20ads_v5"
        STANDARD_E20_AS_V4 = "Standard_E20as_v4"
        STANDARD_E20_AS_V5 = "Standard_E20as_v5"
        STANDARD_E20_AV4 = "Standard_E20a_v4"
        STANDARD_E20_DS_V4 = "Standard_E20ds_v4"
        STANDARD_E20_DS_V5 = "Standard_E20ds_v5"
        STANDARD_E20_DV4 = "Standard_E20d_v4"
        STANDARD_E20_DV5 = "Standard_E20d_v5"
        STANDARD_E20_SV3 = "Standard_E20s_v3"
        STANDARD_E20_SV4 = "Standard_E20s_v4"
        STANDARD_E20_SV5 = "Standard_E20s_v5"
        STANDARD_E20_V3 = "Standard_E20_v3"
        STANDARD_E20_V4 = "Standard_E20_v4"
        STANDARD_E20_V5 = "Standard_E20_v5"
        STANDARD_E2_ADS_V5 = "Standard_E2ads_v5"
        STANDARD_E2_AS_V4 = "Standard_E2as_v4"
        STANDARD_E2_AS_V5 = "Standard_E2as_v5"
        STANDARD_E2_AV4 = "Standard_E2a_v4"
        STANDARD_E2_BDS_V5 = "Standard_E2bds_v5"
        STANDARD_E2_BS_V5 = "Standard_E2bs_v5"
        STANDARD_E2_DS_V4 = "Standard_E2ds_v4"
        STANDARD_E2_DS_V5 = "Standard_E2ds_v5"
        STANDARD_E2_DV4 = "Standard_E2d_v4"
        STANDARD_E2_DV5 = "Standard_E2d_v5"
        STANDARD_E2_SV3 = "Standard_E2s_v3"
        STANDARD_E2_SV4 = "Standard_E2s_v4"
        STANDARD_E2_SV5 = "Standard_E2s_v5"
        STANDARD_E2_V3 = "Standard_E2_v3"
        STANDARD_E2_V4 = "Standard_E2_v4"
        STANDARD_E2_V5 = "Standard_E2_v5"
        STANDARD_E3216_ADS_V5 = "Standard_E32_16ads_v5"
        STANDARD_E3216_AS_V4 = "Standard_E32_16as_v4"
        STANDARD_E3216_AS_V5 = "Standard_E32_16as_v5"
        STANDARD_E3216_DS_V4 = "Standard_E32_16ds_v4"
        STANDARD_E3216_DS_V5 = "Standard_E32_16ds_v5"
        STANDARD_E3216_SV3 = "Standard_E32_16s_v3"
        STANDARD_E3216_SV4 = "Standard_E32_16s_v4"
        STANDARD_E3216_SV5 = "Standard_E32_16s_v5"
        STANDARD_E328_ADS_V5 = "Standard_E32_8ads_v5"
        STANDARD_E328_AS_V4 = "Standard_E32_8as_v4"
        STANDARD_E328_AS_V5 = "Standard_E32_8as_v5"
        STANDARD_E328_DS_V4 = "Standard_E32_8ds_v4"
        STANDARD_E328_DS_V5 = "Standard_E32_8ds_v5"
        STANDARD_E328_SV3 = "Standard_E32_8s_v3"
        STANDARD_E328_SV4 = "Standard_E32_8s_v4"
        STANDARD_E328_SV5 = "Standard_E32_8s_v5"
        STANDARD_E32_ADS_V5 = "Standard_E32ads_v5"
        STANDARD_E32_AS_V4 = "Standard_E32as_v4"
        STANDARD_E32_AS_V5 = "Standard_E32as_v5"
        STANDARD_E32_AV4 = "Standard_E32a_v4"
        STANDARD_E32_BDS_V5 = "Standard_E32bds_v5"
        STANDARD_E32_BS_V5 = "Standard_E32bs_v5"
        STANDARD_E32_DS_V4 = "Standard_E32ds_v4"
        STANDARD_E32_DS_V5 = "Standard_E32ds_v5"
        STANDARD_E32_DV4 = "Standard_E32d_v4"
        STANDARD_E32_DV5 = "Standard_E32d_v5"
        STANDARD_E32_SV3 = "Standard_E32s_v3"
        STANDARD_E32_SV4 = "Standard_E32s_v4"
        STANDARD_E32_SV5 = "Standard_E32s_v5"
        STANDARD_E32_V3 = "Standard_E32_v3"
        STANDARD_E32_V4 = "Standard_E32_v4"
        STANDARD_E32_V5 = "Standard_E32_v5"
        STANDARD_E42_ADS_V5 = "Standard_E4_2ads_v5"
        STANDARD_E42_AS_V4 = "Standard_E4_2as_v4"
        STANDARD_E42_AS_V5 = "Standard_E4_2as_v5"
        STANDARD_E42_DS_V4 = "Standard_E4_2ds_v4"
        STANDARD_E42_DS_V5 = "Standard_E4_2ds_v5"
        STANDARD_E42_SV3 = "Standard_E4_2s_v3"
        STANDARD_E42_SV4 = "Standard_E4_2s_v4"
        STANDARD_E42_SV5 = "Standard_E4_2s_v5"
        STANDARD_E48_ADS_V5 = "Standard_E48ads_v5"
        STANDARD_E48_AS_V4 = "Standard_E48as_v4"
        STANDARD_E48_AS_V5 = "Standard_E48as_v5"
        STANDARD_E48_AV4 = "Standard_E48a_v4"
        STANDARD_E48_BDS_V5 = "Standard_E48bds_v5"
        STANDARD_E48_BS_V5 = "Standard_E48bs_v5"
        STANDARD_E48_DS_V4 = "Standard_E48ds_v4"
        STANDARD_E48_DS_V5 = "Standard_E48ds_v5"
        STANDARD_E48_DV4 = "Standard_E48d_v4"
        STANDARD_E48_DV5 = "Standard_E48d_v5"
        STANDARD_E48_SV3 = "Standard_E48s_v3"
        STANDARD_E48_SV4 = "Standard_E48s_v4"
        STANDARD_E48_SV5 = "Standard_E48s_v5"
        STANDARD_E48_V3 = "Standard_E48_v3"
        STANDARD_E48_V4 = "Standard_E48_v4"
        STANDARD_E48_V5 = "Standard_E48_v5"
        STANDARD_E4_ADS_V5 = "Standard_E4ads_v5"
        STANDARD_E4_AS_V4 = "Standard_E4as_v4"
        STANDARD_E4_AS_V5 = "Standard_E4as_v5"
        STANDARD_E4_AV4 = "Standard_E4a_v4"
        STANDARD_E4_BDS_V5 = "Standard_E4bds_v5"
        STANDARD_E4_BS_V5 = "Standard_E4bs_v5"
        STANDARD_E4_DS_V4 = "Standard_E4ds_v4"
        STANDARD_E4_DS_V5 = "Standard_E4ds_v5"
        STANDARD_E4_DV4 = "Standard_E4d_v4"
        STANDARD_E4_DV5 = "Standard_E4d_v5"
        STANDARD_E4_SV3 = "Standard_E4s_v3"
        STANDARD_E4_SV4 = "Standard_E4s_v4"
        STANDARD_E4_SV5 = "Standard_E4s_v5"
        STANDARD_E4_V3 = "Standard_E4_v3"
        STANDARD_E4_V4 = "Standard_E4_v4"
        STANDARD_E4_V5 = "Standard_E4_v5"
        STANDARD_E6416_ADS_V5 = "Standard_E64_16ads_v5"
        STANDARD_E6416_AS_V4 = "Standard_E64_16as_v4"
        STANDARD_E6416_AS_V5 = "Standard_E64_16as_v5"
        STANDARD_E6416_DS_V4 = "Standard_E64_16ds_v4"
        STANDARD_E6416_DS_V5 = "Standard_E64_16ds_v5"
        STANDARD_E6416_SV3 = "Standard_E64_16s_v3"
        STANDARD_E6416_SV4 = "Standard_E64_16s_v4"
        STANDARD_E6416_SV5 = "Standard_E64_16s_v5"
        STANDARD_E6432_ADS_V5 = "Standard_E64_32ads_v5"
        STANDARD_E6432_AS_V4 = "Standard_E64_32as_v4"
        STANDARD_E6432_AS_V5 = "Standard_E64_32as_v5"
        STANDARD_E6432_DS_V4 = "Standard_E64_32ds_v4"
        STANDARD_E6432_DS_V5 = "Standard_E64_32ds_v5"
        STANDARD_E6432_SV3 = "Standard_E64_32s_v3"
        STANDARD_E6432_SV4 = "Standard_E64_32s_v4"
        STANDARD_E6432_SV5 = "Standard_E64_32s_v5"
        STANDARD_E64_ADS_V5 = "Standard_E64ads_v5"
        STANDARD_E64_AS_V4 = "Standard_E64as_v4"
        STANDARD_E64_AS_V5 = "Standard_E64as_v5"
        STANDARD_E64_AV4 = "Standard_E64a_v4"
        STANDARD_E64_BDS_V5 = "Standard_E64bds_v5"
        STANDARD_E64_BS_V5 = "Standard_E64bs_v5"
        STANDARD_E64_DS_V4 = "Standard_E64ds_v4"
        STANDARD_E64_DS_V5 = "Standard_E64ds_v5"
        STANDARD_E64_DV4 = "Standard_E64d_v4"
        STANDARD_E64_DV5 = "Standard_E64d_v5"
        STANDARD_E64_IS_V3 = "Standard_E64is_v3"
        STANDARD_E64_IV3 = "Standard_E64i_v3"
        STANDARD_E64_SV3 = "Standard_E64s_v3"
        STANDARD_E64_SV4 = "Standard_E64s_v4"
        STANDARD_E64_SV5 = "Standard_E64s_v5"
        STANDARD_E64_V3 = "Standard_E64_v3"
        STANDARD_E64_V4 = "Standard_E64_v4"
        STANDARD_E64_V5 = "Standard_E64_v5"
        STANDARD_E80_IDS_V4 = "Standard_E80ids_v4"
        STANDARD_E80_IS_V4 = "Standard_E80is_v4"
        STANDARD_E82_ADS_V5 = "Standard_E8_2ads_v5"
        STANDARD_E82_AS_V4 = "Standard_E8_2as_v4"
        STANDARD_E82_AS_V5 = "Standard_E8_2as_v5"
        STANDARD_E82_DS_V4 = "Standard_E8_2ds_v4"
        STANDARD_E82_DS_V5 = "Standard_E8_2ds_v5"
        STANDARD_E82_SV3 = "Standard_E8_2s_v3"
        STANDARD_E82_SV4 = "Standard_E8_2s_v4"
        STANDARD_E82_SV5 = "Standard_E8_2s_v5"
        STANDARD_E84_ADS_V5 = "Standard_E8_4ads_v5"
        STANDARD_E84_AS_V4 = "Standard_E8_4as_v4"
        STANDARD_E84_AS_V5 = "Standard_E8_4as_v5"
        STANDARD_E84_DS_V4 = "Standard_E8_4ds_v4"
        STANDARD_E84_DS_V5 = "Standard_E8_4ds_v5"
        STANDARD_E84_SV3 = "Standard_E8_4s_v3"
        STANDARD_E84_SV4 = "Standard_E8_4s_v4"
        STANDARD_E84_SV5 = "Standard_E8_4s_v5"
        STANDARD_E8_ADS_V5 = "Standard_E8ads_v5"
        STANDARD_E8_AS_V4 = "Standard_E8as_v4"
        STANDARD_E8_AS_V5 = "Standard_E8as_v5"
        STANDARD_E8_AV4 = "Standard_E8a_v4"
        STANDARD_E8_BDS_V5 = "Standard_E8bds_v5"
        STANDARD_E8_BS_V5 = "Standard_E8bs_v5"
        STANDARD_E8_DS_V4 = "Standard_E8ds_v4"
        STANDARD_E8_DS_V5 = "Standard_E8ds_v5"
        STANDARD_E8_DV4 = "Standard_E8d_v4"
        STANDARD_E8_DV5 = "Standard_E8d_v5"
        STANDARD_E8_SV3 = "Standard_E8s_v3"
        STANDARD_E8_SV4 = "Standard_E8s_v4"
        STANDARD_E8_SV5 = "Standard_E8s_v5"
        STANDARD_E8_V3 = "Standard_E8_v3"
        STANDARD_E8_V4 = "Standard_E8_v4"
        STANDARD_E8_V5 = "Standard_E8_v5"
        STANDARD_E9624_ADS_V5 = "Standard_E96_24ads_v5"
        STANDARD_E9624_AS_V4 = "Standard_E96_24as_v4"
        STANDARD_E9624_AS_V5 = "Standard_E96_24as_v5"
        STANDARD_E9624_DS_V5 = "Standard_E96_24ds_v5"
        STANDARD_E9624_SV5 = "Standard_E96_24s_v5"
        STANDARD_E9648_ADS_V5 = "Standard_E96_48ads_v5"
        STANDARD_E9648_AS_V4 = "Standard_E96_48as_v4"
        STANDARD_E9648_AS_V5 = "Standard_E96_48as_v5"
        STANDARD_E9648_DS_V5 = "Standard_E96_48ds_v5"
        STANDARD_E9648_SV5 = "Standard_E96_48s_v5"
        STANDARD_E96_ADS_V5 = "Standard_E96ads_v5"
        STANDARD_E96_AS_V4 = "Standard_E96as_v4"
        STANDARD_E96_AS_V5 = "Standard_E96as_v5"
        STANDARD_E96_AV4 = "Standard_E96a_v4"
        STANDARD_E96_DS_V5 = "Standard_E96ds_v5"
        STANDARD_E96_DV5 = "Standard_E96d_v5"
        STANDARD_E96_SV5 = "Standard_E96s_v5"
        STANDARD_E96_V5 = "Standard_E96_v5"
        STANDARD_F1 = "Standard_F1"
        STANDARD_F16 = "Standard_F16"
        STANDARD_F16_S = "Standard_F16s"
        STANDARD_F16_SV2 = "Standard_F16s_v2"
        STANDARD_F1_S = "Standard_F1s"
        STANDARD_F2 = "Standard_F2"
        STANDARD_F2_S = "Standard_F2s"
        STANDARD_F2_SV2 = "Standard_F2s_v2"
        STANDARD_F32_SV2 = "Standard_F32s_v2"
        STANDARD_F4 = "Standard_F4"
        STANDARD_F48_SV2 = "Standard_F48s_v2"
        STANDARD_F4_S = "Standard_F4s"
        STANDARD_F4_SV2 = "Standard_F4s_v2"
        STANDARD_F64_SV2 = "Standard_F64s_v2"
        STANDARD_F72_SV2 = "Standard_F72s_v2"
        STANDARD_F8 = "Standard_F8"
        STANDARD_F8_S = "Standard_F8s"
        STANDARD_F8_SV2 = "Standard_F8s_v2"
        STANDARD_G1 = "Standard_G1"
        STANDARD_G2 = "Standard_G2"
        STANDARD_G3 = "Standard_G3"
        STANDARD_G4 = "Standard_G4"
        STANDARD_G5 = "Standard_G5"
        STANDARD_GS1 = "Standard_GS1"
        STANDARD_GS2 = "Standard_GS2"
        STANDARD_GS3 = "Standard_GS3"
        STANDARD_GS4 = "Standard_GS4"
        STANDARD_GS44 = "Standard_GS4_4"
        STANDARD_GS48 = "Standard_GS4_8"
        STANDARD_GS5 = "Standard_GS5"
        STANDARD_GS516 = "Standard_GS5_16"
        STANDARD_GS58 = "Standard_GS5_8"
        STANDARD_H16 = "Standard_H16"
        STANDARD_H16_M = "Standard_H16m"
        STANDARD_H16_MR = "Standard_H16mr"
        STANDARD_H16_R = "Standard_H16r"
        STANDARD_H8 = "Standard_H8"
        STANDARD_H8_M = "Standard_H8m"
        STANDARD_L16_S = "Standard_L16s"
        STANDARD_L16_SV2 = "Standard_L16s_v2"
        STANDARD_L32_S = "Standard_L32s"
        STANDARD_L32_SV2 = "Standard_L32s_v2"
        STANDARD_L48_SV2 = "Standard_L48s_v2"
        STANDARD_L4_S = "Standard_L4s"
        STANDARD_L64_SV2 = "Standard_L64s_v2"
        STANDARD_L80_SV2 = "Standard_L80s_v2"
        STANDARD_L8_S = "Standard_L8s"
        STANDARD_L8_SV2 = "Standard_L8s_v2"
        STANDARD_M128 = "Standard_M128"
        STANDARD_M12832_MS = "Standard_M128_32ms"
        STANDARD_M12864_MS = "Standard_M128_64ms"
        STANDARD_M128_DMS_V2 = "Standard_M128dms_v2"
        STANDARD_M128_DS_V2 = "Standard_M128ds_v2"
        STANDARD_M128_M = "Standard_M128m"
        STANDARD_M128_MS = "Standard_M128ms"
        STANDARD_M128_MS_V2 = "Standard_M128ms_v2"
        STANDARD_M128_S = "Standard_M128s"
        STANDARD_M128_SV2 = "Standard_M128s_v2"
        STANDARD_M164_MS = "Standard_M16_4ms"
        STANDARD_M168_MS = "Standard_M16_8ms"
        STANDARD_M16_MS = "Standard_M16ms"
        STANDARD_M192_IDMS_V2 = "Standard_M192idms_v2"
        STANDARD_M192_IDS_V2 = "Standard_M192ids_v2"
        STANDARD_M192_IMS_V2 = "Standard_M192ims_v2"
        STANDARD_M192_IS_V2 = "Standard_M192is_v2"
        STANDARD_M208_MS_V2 = "Standard_M208ms_v2"
        STANDARD_M208_SV2 = "Standard_M208s_v2"
        STANDARD_M3216_MS = "Standard_M32_16ms"
        STANDARD_M328_MS = "Standard_M32_8ms"
        STANDARD_M32_DMS_V2 = "Standard_M32dms_v2"
        STANDARD_M32_LS = "Standard_M32ls"
        STANDARD_M32_MS = "Standard_M32ms"
        STANDARD_M32_MS_V2 = "Standard_M32ms_v2"
        STANDARD_M32_TS = "Standard_M32ts"
        STANDARD_M416208_MS_V2 = "Standard_M416_208ms_v2"
        STANDARD_M416208_SV2 = "Standard_M416_208s_v2"
        STANDARD_M416_MS_V2 = "Standard_M416ms_v2"
        STANDARD_M416_SV2 = "Standard_M416s_v2"
        STANDARD_M64 = "Standard_M64"
        STANDARD_M6416_MS = "Standard_M64_16ms"
        STANDARD_M6432_MS = "Standard_M64_32ms"
        STANDARD_M64_DMS_V2 = "Standard_M64dms_v2"
        STANDARD_M64_DS_V2 = "Standard_M64ds_v2"
        STANDARD_M64_LS = "Standard_M64ls"
        STANDARD_M64_M = "Standard_M64m"
        STANDARD_M64_MS = "Standard_M64ms"
        STANDARD_M64_MS_V2 = "Standard_M64ms_v2"
        STANDARD_M64_S = "Standard_M64s"
        STANDARD_M64_SV2 = "Standard_M64s_v2"
        STANDARD_M82_MS = "Standard_M8_2ms"
        STANDARD_M84_MS = "Standard_M8_4ms"
        STANDARD_M8_MS = "Standard_M8ms"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.AzureVmSuitabilityDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANNOT_REPORT_BANDWIDTH_COSTS = "CannotReportBandwidthCosts"
        CANNOT_REPORT_COMPUTE_COST = "CannotReportComputeCost"
        CANNOT_REPORT_STORAGE_COST = "CannotReportStorageCost"
        NONE = "None"
        PERCENTAGE_OF_CORES_UTILIZED_MISSING = "PercentageOfCoresUtilizedMissing"
        PERCENTAGE_OF_CORES_UTILIZED_OUT_OF_RANGE = "PercentageOfCoresUtilizedOutOfRange"
        PERCENTAGE_OF_MEMORY_UTILIZED_MISSING = "PercentageOfMemoryUtilizedMissing"
        PERCENTAGE_OF_MEMORY_UTILIZED_OUT_OF_RANGE = "PercentageOfMemoryUtilizedOutOfRange"
        RECOMMENDED_SIZE_HAS_LESS_NETWORK_ADAPTERS = "RecommendedSizeHasLessNetworkAdapters"


    class azure.mgmt.migrationassessment.models.AzureVmSuitabilityExplanation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOT_TYPE_NOT_SUPPORTED = "BootTypeNotSupported"
        BOOT_TYPE_UNKNOWN = "BootTypeUnknown"
        CHECK_CENT_OS_VERSION = "CheckCentOsVersion"
        CHECK_CORE_OS_LINUX_VERSION = "CheckCoreOsLinuxVersion"
        CHECK_DEBIAN_LINUX_VERSION = "CheckDebianLinuxVersion"
        CHECK_OPEN_SUSE_LINUX_VERSION = "CheckOpenSuseLinuxVersion"
        CHECK_ORACLE_LINUX_VERSION = "CheckOracleLinuxVersion"
        CHECK_RED_HAT_LINUX_VERSION = "CheckRedHatLinuxVersion"
        CHECK_SUSE_LINUX_VERSION = "CheckSuseLinuxVersion"
        CHECK_UBUNTU_LINUX_VERSION = "CheckUbuntuLinuxVersion"
        CHECK_WINDOWS_SERVER2008_R2_VERSION = "CheckWindowsServer2008R2Version"
        ENDORSED_WITH_CONDITIONS_LINUX_DISTRIBUTIONS = "EndorsedWithConditionsLinuxDistributions"
        GUEST_OPERATING_SYSTEM_ARCHITECTURE_NOT_SUPPORTED = "GuestOperatingSystemArchitectureNotSupported"
        GUEST_OPERATING_SYSTEM_NOT_SUPPORTED = "GuestOperatingSystemNotSupported"
        GUEST_OPERATING_SYSTEM_UNKNOWN = "GuestOperatingSystemUnknown"
        INTERNAL_ERROR_OCCURRED_DURING_COMPUTE_EVALUATION = "InternalErrorOccurredDuringComputeEvaluation"
        INTERNAL_ERROR_OCCURRED_DURING_NETWORK_EVALUATION = "InternalErrorOccurredDuringNetworkEvaluation"
        INTERNAL_ERROR_OCCURRED_DURING_STORAGE_EVALUATION = "InternalErrorOccurredDuringStorageEvaluation"
        MORE_DISKS_THAN_SUPPORTED = "MoreDisksThanSupported"
        NOT_APPLICABLE = "NotApplicable"
        NO_EA_PRICE_FOUND_FOR_VM_SIZE = "NoEaPriceFoundForVmSize"
        NO_GUEST_OPERATING_SYSTEM_CONDITIONALLY_SUPPORTED = "NoGuestOperatingSystemConditionallySupported"
        NO_SUITABLE_VM_SIZE_FOUND = "NoSuitableVmSizeFound"
        NO_VM_SIZE_FOR_BASIC_PRICING_TIER = "NoVmSizeForBasicPricingTier"
        NO_VM_SIZE_FOR_SELECTED_AZURE_LOCATION = "NoVmSizeForSelectedAzureLocation"
        NO_VM_SIZE_FOR_SELECTED_PRICING_TIER = "NoVmSizeForSelectedPricingTier"
        NO_VM_SIZE_FOR_STANDARD_PRICING_TIER = "NoVmSizeForStandardPricingTier"
        NO_VM_SIZE_FOUND_FOR_OFFER_CURRENCY_RESERVED_INSTANCE = "NoVmSizeFoundForOfferCurrencyReservedInstance"
        NO_VM_SIZE_IN_SELECTED_FAMILY_FOUND = "NoVmSizeInSelectedFamilyFound"
        NO_VM_SIZE_SUPPORTS_NETWORK_PERFORMANCE = "NoVmSizeSupportsNetworkPerformance"
        NO_VM_SIZE_SUPPORTS_STORAGE_PERFORMANCE = "NoVmSizeSupportsStoragePerformance"
        ONE_OR_MORE_ADAPTERS_NOT_SUITABLE = "OneOrMoreAdaptersNotSuitable"
        ONE_OR_MORE_DISKS_NOT_SUITABLE = "OneOrMoreDisksNotSuitable"
        UNENDORSED_LINUX_DISTRIBUTIONS = "UnendorsedLinuxDistributions"
        UNKNOWN = "Unknown"
        WINDOWS_CLIENT_VERSIONS_CONDITIONALLY_SUPPORTED = "WindowsClientVersionsConditionallySupported"
        WINDOWS_OS_NO_LONGER_UNDER_MS_SUPPORT = "WindowsOSNoLongerUnderMSSupport"
        WINDOWS_SERVER_VERSIONS_SUPPORTED_WITH_CAVEAT = "WindowsServerVersionsSupportedWithCaveat"
        WINDOWS_SERVER_VERSION_CONDITIONALLY_SUPPORTED = "WindowsServerVersionConditionallySupported"


    class azure.mgmt.migrationassessment.models.CloudSuitability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONALLY_SUITABLE = "ConditionallySuitable"
        NOT_SUITABLE = "NotSuitable"
        READINESS_UNKNOWN = "ReadinessUnknown"
        SUITABLE = "Suitable"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.CollectorAgentPropertiesBase(Model):
        id: str
        last_heartbeat_utc: datetime
        spn_details: CollectorAgentSpnPropertiesBase
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                last_heartbeat_utc: Optional[datetime] = ..., 
                spn_details: Optional[CollectorAgentSpnPropertiesBase] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.CollectorAgentSpnPropertiesBase(Model):
        application_id: str
        audience: str
        authority: str
        object_id: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                authority: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.CollectorPropertiesBase(AzureResourceProperties):
        created_timestamp: datetime
        discovery_site_id: str
        provisioning_state: Union[str, ProvisioningState]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                discovery_site_id: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.CollectorPropertiesBaseWithAgent(AzureResourceProperties):
        agent_properties: CollectorAgentPropertiesBase
        created_timestamp: datetime
        discovery_site_id: str
        provisioning_state: Union[str, ProvisioningState]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_properties: Optional[CollectorAgentPropertiesBase] = ..., 
                discovery_site_id: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.CompatibilityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPAT_LEVEL100 = "CompatLevel100"
        COMPAT_LEVEL110 = "CompatLevel110"
        COMPAT_LEVEL120 = "CompatLevel120"
        COMPAT_LEVEL130 = "CompatLevel130"
        COMPAT_LEVEL140 = "CompatLevel140"
        COMPAT_LEVEL150 = "CompatLevel150"
        COMPAT_LEVEL80 = "CompatLevel80"
        COMPAT_LEVEL90 = "CompatLevel90"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.ComputeTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        PROVISIONED = "Provisioned"
        SERVERLESS = "Serverless"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.CostComponent(Model):
        description: str
        name: Union[str, CostComponentName]
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.CostComponentName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY_AZURE_HYBRID_COST_SAVINGS = "MonthlyAzureHybridCostSavings"
        MONTHLY_PREMIUM_V2_STORAGE_COST = "MonthlyPremiumV2StorageCost"
        MONTHLY_SECURITY_COST = "MonthlySecurityCost"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.migrationassessment.models.Disk(Model):
        display_name: str
        gigabytes_allocated: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.DownloadUrl(Model):
        assessment_report_url: str
        expiration_time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.EntityUptime(Model):
        days_per_month: int
        hours_per_day: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_per_month: Optional[int] = ..., 
                hours_per_day: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.EnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRODUCTION = "Production"
        TEST = "Test"


    class azure.mgmt.migrationassessment.models.Error(Model):
        agent_scenario: str
        appliance_name: str
        code: str
        id: int
        impacted_assessment_type: str
        message: str
        message_parameters: dict[str, str]
        possible_causes: str
        recommended_action: str
        run_as_account_id: str
        severity: str
        summary_message: str
        updated_time_stamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ErrorDetail(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ErrorResponse(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ErrorSummary(Model):
        assessment_type: Union[str, AssessmentType]
        count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.FttAndRaidLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FTT1_RAID1 = "Ftt1Raid1"
        FTT1_RAID5 = "Ftt1Raid5"
        FTT2_RAID1 = "Ftt2Raid1"
        FTT2_RAID6 = "Ftt2Raid6"
        FTT3_RAID1 = "Ftt3Raid1"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.Group(ProxyResource):
        id: str
        name: str
        properties: GroupProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[GroupProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.GroupBodyProperties(Model):
        machines: list[str]
        operation_type: Union[str, GroupUpdateOperation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                machines: Optional[List[str]] = ..., 
                operation_type: Optional[Union[str, GroupUpdateOperation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.GroupListResult(Model):
        next_link: str
        value: list[Group]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Group], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.GroupProperties(AzureResourceProperties):
        are_assessments_running: bool
        assessments: list[str]
        created_timestamp: datetime
        group_status: Union[str, GroupStatus]
        group_type: Union[str, GroupType]
        machine_count: int
        provisioning_state: Union[str, ProvisioningState]
        supported_assessment_types: Union[list[str, AssessmentType]]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_type: Optional[Union[str, GroupType]] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                supported_assessment_types: Optional[List[Union[str, AssessmentType]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.GroupStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        CREATED = "Created"
        INVALID = "Invalid"
        RUNNING = "Running"
        UPDATED = "Updated"


    class azure.mgmt.migrationassessment.models.GroupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        IMPORT = "Import"
        IMPORT_ENUM = "Import"


    class azure.mgmt.migrationassessment.models.GroupUpdateOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "Add"
        REMOVE = "Remove"


    class azure.mgmt.migrationassessment.models.GuestOperatingSystemArchitecture(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UNKNOWN = "Unknown"
        X64 = "X64"
        X86 = "X86"


    class azure.mgmt.migrationassessment.models.HardwareGeneration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        DC_SERIES = "DC_series"
        FSV2_SERIES = "Fsv2_series"
        GEN5 = "Gen5"
        M_SERIES = "M_series"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.HypervCollector(ProxyResource):
        id: str
        name: str
        properties: CollectorPropertiesBaseWithAgent
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CollectorPropertiesBaseWithAgent] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.HypervCollectorListResult(Model):
        next_link: str
        value: list[HypervCollector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[HypervCollector], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ImpactedAssessmentObject(Model):
        object_name: str
        object_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ImportCollector(ProxyResource):
        id: str
        name: str
        properties: CollectorPropertiesBase
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CollectorPropertiesBase] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ImportCollectorListResult(Model):
        next_link: str
        value: list[ImportCollector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ImportCollector], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.Machine(ProxyResource):
        id: str
        name: str
        properties: MachineProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MachineProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.MachineAssessmentProperties(AzureResourceProperties):
        assessment_error_summary: dict[str, int]
        assessment_type: Union[str, AssessmentType]
        azure_disk_types: Union[list[str, AzureDiskType]]
        azure_hybrid_use_benefit: Union[str, AzureHybridUseBenefit]
        azure_location: str
        azure_offer_code: Union[str, AzureOfferCode]
        azure_pricing_tier: Union[str, AzurePricingTier]
        azure_storage_redundancy: Union[str, AzureStorageRedundancy]
        azure_vm_families: Union[list[str, AzureVmFamily]]
        confidence_rating_in_percentage: float
        cost_components: list[CostComponent]
        created_timestamp: datetime
        currency: Union[str, AzureCurrency]
        discount_percentage: float
        distribution_by_os_name: dict[str, int]
        distribution_by_service_pack_insight: dict[str, int]
        distribution_by_support_status: dict[str, int]
        ea_subscription_id: str
        group_type: Union[str, GroupType]
        monthly_bandwidth_cost: float
        monthly_compute_cost: float
        monthly_premium_storage_cost: float
        monthly_standard_ssd_storage_cost: float
        monthly_storage_cost: float
        monthly_ultra_storage_cost: float
        number_of_machines: int
        percentile: Union[str, Percentile]
        perf_data_end_time: datetime
        perf_data_start_time: datetime
        prices_timestamp: datetime
        provisioning_state: Union[str, ProvisioningState]
        reserved_instance: Union[str, AzureReservedInstance]
        scaling_factor: float
        schema_version: str
        sizing_criterion: Union[str, AssessmentSizingCriterion]
        stage: Union[str, AssessmentStage]
        status: Union[str, AssessmentStatus]
        suitability_summary: dict[str, int]
        time_range: Union[str, TimeRange]
        updated_timestamp: datetime
        vm_uptime: VmUptime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_disk_types: Optional[List[Union[str, AzureDiskType]]] = ..., 
                azure_hybrid_use_benefit: Optional[Union[str, AzureHybridUseBenefit]] = ..., 
                azure_location: Optional[str] = ..., 
                azure_offer_code: Optional[Union[str, AzureOfferCode]] = ..., 
                azure_pricing_tier: Optional[Union[str, AzurePricingTier]] = ..., 
                azure_storage_redundancy: Optional[Union[str, AzureStorageRedundancy]] = ..., 
                azure_vm_families: Optional[List[Union[str, AzureVmFamily]]] = ..., 
                currency: Optional[Union[str, AzureCurrency]] = ..., 
                discount_percentage: Optional[float] = ..., 
                ea_subscription_id: Optional[str] = ..., 
                percentile: Optional[Union[str, Percentile]] = ..., 
                perf_data_end_time: Optional[datetime] = ..., 
                perf_data_start_time: Optional[datetime] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                reserved_instance: Optional[Union[str, AzureReservedInstance]] = ..., 
                scaling_factor: Optional[float] = ..., 
                sizing_criterion: Optional[Union[str, AssessmentSizingCriterion]] = ..., 
                time_range: Optional[Union[str, TimeRange]] = ..., 
                vm_uptime: Optional[VmUptime] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.MachineBootType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIOS = "BIOS"
        EFI = "EFI"
        NOT_SPECIFIED = "NotSpecified"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.MachineListResult(Model):
        next_link: str
        value: list[Machine]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[Machine], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.MachineProperties(Model):
        boot_type: Union[str, MachineBootType]
        created_timestamp: datetime
        datacenter_management_server_arm_id: str
        datacenter_management_server_name: str
        description: str
        discovery_machine_arm_id: str
        disks: dict[str, Disk]
        display_name: str
        errors: list[Error]
        groups: list[str]
        host_processor: ProcessorInfo
        megabytes_of_memory: float
        network_adapters: dict[str, NetworkAdapter]
        number_of_cores: int
        operating_system_name: str
        operating_system_type: str
        operating_system_version: str
        product_support_status: ProductSupportStatus
        sql_instances: list[str]
        updated_timestamp: datetime
        web_applications: list[str]
        workload_summary: WorkloadSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.MigrationGuidelineContext(Model):
        context_key: str
        context_value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                context_key: Optional[str] = ..., 
                context_value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.MultiSubnetIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISASTER_RECOVERY = "DisasterRecovery"
        HIGH_AVAILABILITY = "HighAvailability"
        NONE = "None"


    class azure.mgmt.migrationassessment.models.NetworkAdapter(Model):
        display_name: str
        ip_addresses: list[str]
        mac_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.OperationDisplay(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.OptimizationLogic(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MINIMIZE_COST = "MinimizeCost"
        MODERNIZE_TO_AZURE_SQL_DB = "ModernizeToAzureSqlDb"
        MODERNIZE_TO_AZURE_SQL_MI = "ModernizeToAzureSqlMi"
        MODERNIZE_TO_PAA_S = "ModernizeToPaaS"


    class azure.mgmt.migrationassessment.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.migrationassessment.models.OsLicense(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        UNKNOWN = "Unknown"
        YES = "Yes"


    class azure.mgmt.migrationassessment.models.Percentile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERCENTILE50 = "Percentile50"
        PERCENTILE90 = "Percentile90"
        PERCENTILE95 = "Percentile95"
        PERCENTILE99 = "Percentile99"


    class azure.mgmt.migrationassessment.models.PrivateEndpoint(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.PrivateEndpointConnectionListResult(Model):
        next_link: str
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[PrivateEndpointConnection], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.PrivateEndpointConnectionProperties(Model):
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.migrationassessment.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.migrationassessment.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.PrivateLinkResourceListResult(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[PrivateLinkResource], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.PrivateLinkResourceProperties(Model):
        group_id: str
        required_members: list[str]
        required_zone_names: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required_zone_names: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ProcessorInfo(Model):
        name: str
        number_of_cores_per_socket: int
        number_of_sockets: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                number_of_cores_per_socket: Optional[int] = ..., 
                number_of_sockets: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ProductSupportStatus(Model):
        current_esu_year: str
        current_version: str
        esu_status: str
        eta: int
        extended_security_update_year1_end_date: datetime
        extended_security_update_year2_end_date: datetime
        extended_security_update_year3_end_date: datetime
        extended_support_end_date: datetime
        mainstream_end_date: datetime
        service_pack_status: str
        support_status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ProjectProperties(AzureResourceProperties):
        assessment_solution_id: str
        created_timestamp: datetime
        customer_storage_account_arm_id: str
        customer_workspace_id: str
        customer_workspace_location: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        project_status: Union[str, ProjectStatus]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: str
        service_endpoint: str
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_solution_id: Optional[str] = ..., 
                customer_storage_account_arm_id: Optional[str] = ..., 
                customer_workspace_id: Optional[str] = ..., 
                customer_workspace_location: Optional[str] = ..., 
                project_status: Optional[Union[str, ProjectStatus]] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                public_network_access: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ProjectStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.migrationassessment.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.migrationassessment.models.ProxyResource(Resource):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.RecommendedSuitability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONALLY_SUITABLE_FOR_SQL_DB = "ConditionallySuitableForSqlDB"
        CONDITIONALLY_SUITABLE_FOR_SQL_MI = "ConditionallySuitableForSqlMI"
        CONDITIONALLY_SUITABLE_FOR_SQL_VM = "ConditionallySuitableForSqlVM"
        CONDITIONALLY_SUITABLE_FOR_VM = "ConditionallySuitableForVM"
        NOT_SUITABLE = "NotSuitable"
        POTENTIALLY_SUITABLE_FOR_VM = "PotentiallySuitableForVM"
        READINESS_UNKNOWN = "ReadinessUnknown"
        SUITABLE_FOR_SQL_DB = "SuitableForSqlDB"
        SUITABLE_FOR_SQL_MI = "SuitableForSqlMI"
        SUITABLE_FOR_SQL_VM = "SuitableForSqlVM"
        SUITABLE_FOR_VM = "SuitableForVM"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.Resource(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ResourceId(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ServerCollector(ProxyResource):
        id: str
        name: str
        properties: CollectorPropertiesBaseWithAgent
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CollectorPropertiesBaseWithAgent] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.ServerCollectorListResult(Model):
        next_link: str
        value: list[ServerCollector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ServerCollector], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SharedResourcesDTO(Model):
        number_of_mounts: int
        quorum_witness: AzureQuorumWitnessDTO
        shared_data_disks: list[AzureManagedDiskSkuDTO]
        shared_log_disks: list[AzureManagedDiskSkuDTO]
        shared_temp_db_disks: list[AzureManagedDiskSkuDTO]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SkuReplicationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_GEO_REPLICATION = "ActiveGeoReplication"
        FAILOVER_GROUP_INSTANCE = "FailoverGroupInstance"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.migrationassessment.models.SqlAssessedNetworkAdapter(Model):
        display_name: str
        ip_addresses: list[str]
        mac_address: str
        megabytes_per_second_received: float
        megabytes_per_second_transmitted: float
        monthly_bandwidth_costs: float
        name: str
        net_gigabytes_transmitted_per_month: float
        suitability: Union[str, CloudSuitability]
        suitability_detail: Union[str, AzureNetworkAdapterSuitabilityDetail]
        suitability_explanation: Union[str, AzureNetworkAdapterSuitabilityExplanation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                mac_address: Optional[str] = ..., 
                megabytes_per_second_received: Optional[float] = ..., 
                megabytes_per_second_transmitted: Optional[float] = ..., 
                monthly_bandwidth_costs: Optional[float] = ..., 
                name: Optional[str] = ..., 
                net_gigabytes_transmitted_per_month: Optional[float] = ..., 
                suitability: Optional[Union[str, CloudSuitability]] = ..., 
                suitability_detail: Optional[Union[str, AzureNetworkAdapterSuitabilityDetail]] = ..., 
                suitability_explanation: Optional[Union[str, AzureNetworkAdapterSuitabilityExplanation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentMigrationIssue(Model):
        impacted_objects: list[ImpactedAssessmentObject]
        issue_category: Union[str, SqlAssessmentMigrationIssueCategory]
        issue_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentMigrationIssueCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"
        ISSUE = "Issue"
        WARNING = "Warning"


    class azure.mgmt.migrationassessment.models.SqlAssessmentOptions(ProxyResource):
        id: str
        name: str
        properties: SqlAssessmentOptionsProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SqlAssessmentOptionsProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentOptionsListResult(Model):
        next_link: str
        value: list[SqlAssessmentOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SqlAssessmentOptions], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentOptionsProperties(Model):
        premium_disk_vm_families: Union[list[str, AzureVmFamily]]
        reserved_instance_sql_targets: Union[list[str, TargetType]]
        reserved_instance_supported_currencies: Union[list[str, AzureCurrency]]
        reserved_instance_supported_locations: Union[list[str, AzureLocation]]
        reserved_instance_supported_locations_for_iaas: Union[list[str, AzureLocation]]
        reserved_instance_supported_offers: Union[list[str, AzureOfferCode]]
        reserved_instance_vm_families: Union[list[str, AzureVmFamily]]
        savings_plan_supported_locations: Union[list[str, AzureLocation]]
        savings_plan_supported_locations_for_paas: Union[list[str, AzureLocation]]
        savings_plan_supported_offers: Union[list[str, AzureOfferCode]]
        savings_plan_vm_families: Union[list[str, AzureVmFamily]]
        sql_skus: list[SqlPaaSTargetOptions]
        supported_offers: Union[list[str, AzureOfferCode]]
        vm_families: list[VmFamilyOptions]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reserved_instance_sql_targets: Optional[List[Union[str, TargetType]]] = ..., 
                reserved_instance_supported_currencies: Optional[List[Union[str, AzureCurrency]]] = ..., 
                reserved_instance_supported_locations: Optional[List[Union[str, AzureLocation]]] = ..., 
                reserved_instance_supported_locations_for_iaas: Optional[List[Union[str, AzureLocation]]] = ..., 
                reserved_instance_supported_offers: Optional[List[Union[str, AzureOfferCode]]] = ..., 
                savings_plan_supported_locations: Optional[List[Union[str, AzureLocation]]] = ..., 
                savings_plan_supported_locations_for_paas: Optional[List[Union[str, AzureLocation]]] = ..., 
                savings_plan_supported_offers: Optional[List[Union[str, AzureOfferCode]]] = ..., 
                savings_plan_vm_families: Optional[List[Union[str, AzureVmFamily]]] = ..., 
                sql_skus: Optional[List[SqlPaaSTargetOptions]] = ..., 
                supported_offers: Optional[List[Union[str, AzureOfferCode]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2(ProxyResource):
        id: str
        name: str
        properties: SqlAssessmentV2Properties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SqlAssessmentV2Properties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2IaasSuitabilityData(Model):
        azure_sql_sku: AzureSqlIaasSkuDTO
        cost_components: list[CostComponent]
        migration_guidelines: list[SqlMigrationGuideline]
        migration_issues: list[SqlAssessmentMigrationIssue]
        migration_target_platform: Union[str, TargetType]
        monthly_compute_cost: float
        monthly_storage_cost: float
        recommendation_reasonings: list[SqlRecommendationReasoning]
        replica_azure_sql_sku: list[AzureSqlIaasSkuDTO]
        security_suitability: Union[str, CloudSuitability]
        shared_resources: SharedResourcesDTO
        should_provision_replicas: bool
        sku_replication_mode: Union[str, SkuReplicationMode]
        suitability: Union[str, CloudSuitability]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_components: Optional[List[CostComponent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2ListResult(Model):
        next_link: str
        value: list[SqlAssessmentV2]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SqlAssessmentV2], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2PaasSuitabilityData(Model):
        azure_sql_sku: AzureSqlPaasSkuDTO
        cost_components: list[CostComponent]
        migration_guidelines: list[SqlMigrationGuideline]
        migration_issues: list[SqlAssessmentMigrationIssue]
        migration_target_platform: Union[str, TargetType]
        monthly_compute_cost: float
        monthly_storage_cost: float
        recommendation_reasonings: list[SqlRecommendationReasoning]
        replica_azure_sql_sku: list[AzureSqlPaasSkuDTO]
        security_suitability: Union[str, CloudSuitability]
        shared_resources: SharedResourcesDTO
        should_provision_replicas: bool
        sku_replication_mode: Union[str, SkuReplicationMode]
        suitability: Union[str, CloudSuitability]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cost_components: Optional[List[CostComponent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2Properties(AzureResourceProperties):
        assessment_type: Union[str, AssessmentType]
        async_commit_mode_intent: Union[str, AsyncCommitModeIntent]
        azure_location: str
        azure_offer_code: Union[str, AzureOfferCode]
        azure_offer_code_for_vm: Union[str, AzureOfferCode]
        azure_security_offering_type: Union[str, AzureSecurityOfferingType]
        azure_sql_database_settings: SqlDbSettings
        azure_sql_managed_instance_settings: SqlMiSettings
        azure_sql_vm_settings: SqlVmSettings
        confidence_rating_in_percentage: float
        created_timestamp: datetime
        currency: Union[str, AzureCurrency]
        disaster_recovery_location: Union[str, AzureLocation]
        discount_percentage: float
        ea_subscription_id: str
        enable_hadr_assessment: bool
        entity_uptime: EntityUptime
        environment_type: Union[str, EnvironmentType]
        group_type: Union[str, GroupType]
        is_internet_access_available: bool
        multi_subnet_intent: Union[str, MultiSubnetIntent]
        optimization_logic: Union[str, OptimizationLogic]
        os_license: Union[str, OsLicense]
        percentile: Union[str, Percentile]
        perf_data_end_time: datetime
        perf_data_start_time: datetime
        prices_timestamp: datetime
        provisioning_state: Union[str, ProvisioningState]
        reserved_instance: Union[str, AzureReservedInstance]
        reserved_instance_for_vm: Union[str, AzureReservedInstance]
        scaling_factor: float
        schema_version: str
        sizing_criterion: Union[str, AssessmentSizingCriterion]
        sql_server_license: Union[str, SqlServerLicense]
        stage: Union[str, AssessmentStage]
        status: Union[str, AssessmentStatus]
        time_range: Union[str, TimeRange]
        updated_timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_type: Optional[Union[str, AssessmentType]] = ..., 
                async_commit_mode_intent: Optional[Union[str, AsyncCommitModeIntent]] = ..., 
                azure_location: Optional[str] = ..., 
                azure_offer_code: Optional[Union[str, AzureOfferCode]] = ..., 
                azure_offer_code_for_vm: Optional[Union[str, AzureOfferCode]] = ..., 
                azure_security_offering_type: Optional[Union[str, AzureSecurityOfferingType]] = ..., 
                azure_sql_database_settings: Optional[SqlDbSettings] = ..., 
                azure_sql_managed_instance_settings: Optional[SqlMiSettings] = ..., 
                azure_sql_vm_settings: Optional[SqlVmSettings] = ..., 
                confidence_rating_in_percentage: Optional[float] = ..., 
                currency: Optional[Union[str, AzureCurrency]] = ..., 
                disaster_recovery_location: Optional[Union[str, AzureLocation]] = ..., 
                discount_percentage: Optional[float] = ..., 
                ea_subscription_id: Optional[str] = ..., 
                enable_hadr_assessment: Optional[bool] = ..., 
                entity_uptime: Optional[EntityUptime] = ..., 
                environment_type: Optional[Union[str, EnvironmentType]] = ..., 
                group_type: Optional[Union[str, GroupType]] = ..., 
                is_internet_access_available: Optional[bool] = ..., 
                multi_subnet_intent: Optional[Union[str, MultiSubnetIntent]] = ..., 
                optimization_logic: Optional[Union[str, OptimizationLogic]] = ..., 
                os_license: Optional[Union[str, OsLicense]] = ..., 
                percentile: Optional[Union[str, Percentile]] = ..., 
                perf_data_end_time: Optional[datetime] = ..., 
                perf_data_start_time: Optional[datetime] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                reserved_instance: Optional[Union[str, AzureReservedInstance]] = ..., 
                reserved_instance_for_vm: Optional[Union[str, AzureReservedInstance]] = ..., 
                scaling_factor: Optional[float] = ..., 
                sizing_criterion: Optional[Union[str, AssessmentSizingCriterion]] = ..., 
                sql_server_license: Optional[Union[str, SqlServerLicense]] = ..., 
                time_range: Optional[Union[str, TimeRange]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2Summary(ProxyResource):
        id: str
        name: str
        properties: SqlAssessmentV2SummaryProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[SqlAssessmentV2SummaryProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2SummaryData(Model):
        confidence_score: float
        monthly_compute_cost: float
        monthly_license_cost: float
        monthly_security_cost: float
        monthly_storage_cost: float
        suitability_summary: dict[str, int]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2SummaryListResult(Model):
        next_link: str
        value: list[SqlAssessmentV2Summary]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SqlAssessmentV2Summary], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAssessmentV2SummaryProperties(Model):
        assessment_summary: dict[str, SqlAssessmentV2SummaryData]
        database_distribution_by_sizing_criterion: dict[str, int]
        distribution_by_service_pack_insight: dict[str, int]
        distribution_by_sql_edition: dict[str, int]
        distribution_by_sql_version: dict[str, int]
        distribution_by_support_status: dict[str, int]
        instance_distribution_by_sizing_criterion: dict[str, int]
        number_of_fci_instances: int
        number_of_machines: int
        number_of_sql_availability_groups: int
        number_of_sql_databases: int
        number_of_sql_instances: int
        number_of_successfully_discovered_sql_instances: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAvailabilityGroupDataOverview(Model):
        availability_group_id: str
        availability_group_name: str
        sql_availability_group_entity_id: str
        sql_availability_group_sds_arm_id: str
        sql_availability_replica_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_group_id: Optional[str] = ..., 
                availability_group_name: Optional[str] = ..., 
                sql_availability_group_entity_id: Optional[str] = ..., 
                sql_availability_group_sds_arm_id: Optional[str] = ..., 
                sql_availability_replica_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlAvailabilityReplicaSummary(Model):
        number_of_asynchronous_non_read_replicas: int
        number_of_asynchronous_read_replicas: int
        number_of_primary_replicas: int
        number_of_synchronous_non_read_replicas: int
        number_of_synchronous_read_replicas: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                number_of_asynchronous_non_read_replicas: Optional[int] = ..., 
                number_of_asynchronous_read_replicas: Optional[int] = ..., 
                number_of_primary_replicas: Optional[int] = ..., 
                number_of_synchronous_non_read_replicas: Optional[int] = ..., 
                number_of_synchronous_read_replicas: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlCollector(ProxyResource):
        id: str
        name: str
        properties: CollectorPropertiesBaseWithAgent
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CollectorPropertiesBaseWithAgent] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlCollectorListResult(Model):
        next_link: str
        value: list[SqlCollector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[SqlCollector], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlDbSettings(Model):
        azure_sql_compute_tier: Union[str, ComputeTier]
        azure_sql_data_base_type: Union[str, AzureSqlDataBaseType]
        azure_sql_purchase_model: Union[str, AzureSqlPurchaseModel]
        azure_sql_service_tier: Union[str, AzureSqlServiceTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_sql_compute_tier: Optional[Union[str, ComputeTier]] = ..., 
                azure_sql_data_base_type: Optional[Union[str, AzureSqlDataBaseType]] = ..., 
                azure_sql_purchase_model: Optional[Union[str, AzureSqlPurchaseModel]] = ..., 
                azure_sql_service_tier: Optional[Union[str, AzureSqlServiceTier]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlFCIMetadata(Model):
        fci_shared_disk_count: int
        is_multi_subnet: bool
        state: Union[str, SqlFCIMetadataState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fci_shared_disk_count: Optional[int] = ..., 
                is_multi_subnet: Optional[bool] = ..., 
                state: Optional[Union[str, SqlFCIMetadataState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlFCIMetadataState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INHERITED = "Inherited"
        INITIALIZING = "Initializing"
        OFFLINE = "Offline"
        OFFLINE_PENDING = "OfflinePending"
        ONLINE = "Online"
        ONLINE_PENDING = "OnlinePending"
        PENDING = "Pending"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.SqlFCIState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        NOT_APPLICABLE = "NotApplicable"
        PASSIVE = "Passive"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.SqlMiSettings(Model):
        azure_sql_instance_type: Union[str, AzureSqlInstanceType]
        azure_sql_service_tier: Union[str, AzureSqlServiceTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_sql_instance_type: Optional[Union[str, AzureSqlInstanceType]] = ..., 
                azure_sql_service_tier: Optional[Union[str, AzureSqlServiceTier]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlMigrationGuideline(Model):
        guideline_id: str
        migration_guideline_category: Union[str, SqlMigrationGuidelineCategory]
        migration_guideline_context: list[MigrationGuidelineContext]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                guideline_id: Optional[str] = ..., 
                migration_guideline_category: Optional[Union[str, SqlMigrationGuidelineCategory]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlMigrationGuidelineCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY_GROUP_GUIDELINE = "AvailabilityGroupGuideline"
        FAILOVER_CLUTER_INSTANCE_GUIDE_LINE = "FailoverCluterInstanceGuideLine"
        GENERAL = "General"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.SqlPaaSTargetOptions(Model):
        compute_tier: Union[str, ComputeTier]
        hardware_generation: Union[str, HardwareGeneration]
        service_tier: Union[str, AzureSqlServiceTier]
        target_locations: Union[list[str, AzureLocation]]
        target_type: Union[str, TargetType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compute_tier: Optional[Union[str, ComputeTier]] = ..., 
                hardware_generation: Optional[Union[str, HardwareGeneration]] = ..., 
                service_tier: Optional[Union[str, AzureSqlServiceTier]] = ..., 
                target_locations: Optional[List[Union[str, AzureLocation]]] = ..., 
                target_type: Optional[Union[str, TargetType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlRecommendationReasoning(Model):
        context_parameters: list[SqlRecommendationReasoningContext]
        reasoning_category: str
        reasoning_id: str
        reasoning_string: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reasoning_category: Optional[str] = ..., 
                reasoning_id: Optional[str] = ..., 
                reasoning_string: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlRecommendationReasoningContext(Model):
        context_key: str
        context_value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                context_key: Optional[str] = ..., 
                context_value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SqlServerLicense(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        UNKNOWN = "Unknown"
        YES = "Yes"


    class azure.mgmt.migrationassessment.models.SqlVmSettings(Model):
        instance_series: Union[list[str, AzureVmFamily]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_series: Optional[List[Union[str, AzureVmFamily]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.SystemData(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.TargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SQL_DATABASE = "AzureSqlDatabase"
        AZURE_SQL_MANAGED_INSTANCE = "AzureSqlManagedInstance"
        AZURE_SQL_VIRTUAL_MACHINE = "AzureSqlVirtualMachine"
        AZURE_VIRTUAL_MACHINE = "AzureVirtualMachine"
        RECOMMENDED = "Recommended"
        UNKNOWN = "Unknown"


    class azure.mgmt.migrationassessment.models.TimeRange(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        DAY = "Day"
        MONTH = "Month"
        WEEK = "Week"


    class azure.mgmt.migrationassessment.models.TrackedResource(Resource):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.UltraDiskAssessmentOptions(Model):
        family_name: str
        target_locations: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                family_name: Optional[str] = ..., 
                target_locations: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.UpdateGroupBody(Model):
        e_tag: str
        properties: GroupBodyProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                e_tag: Optional[str] = ..., 
                properties: Optional[GroupBodyProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.VmFamilyOptions(Model):
        category: list[str]
        family_name: str
        target_locations: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.VmUptime(Model):
        days_per_month: int
        hours_per_day: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_per_month: Optional[int] = ..., 
                hours_per_day: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.VmwareCollector(ProxyResource):
        id: str
        name: str
        properties: CollectorPropertiesBaseWithAgent
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[CollectorPropertiesBaseWithAgent] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.VmwareCollectorListResult(Model):
        next_link: str
        value: list[VmwareCollector]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[VmwareCollector], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.migrationassessment.models.WorkloadSummary(Model):
        oracle_instances: int
        spring_apps: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                oracle_instances: Optional[int] = ..., 
                spring_apps: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.migrationassessment.operations

    class azure.mgmt.migrationassessment.operations.AssessedMachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_machine_name: str, 
                **kwargs: Any
            ) -> AssessedMachine: ...

        @distributed_trace
        def list_by_assessment(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AssessedMachine]: ...


    class azure.mgmt.migrationassessment.operations.AssessedSqlDatabaseV2OperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_sql_database_name: str, 
                **kwargs: Any
            ) -> AssessedSqlDatabaseV2: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AssessedSqlDatabaseV2]: ...


    class azure.mgmt.migrationassessment.operations.AssessedSqlInstanceV2OperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_sql_instance_name: str, 
                **kwargs: Any
            ) -> AssessedSqlInstanceV2: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AssessedSqlInstanceV2]: ...


    class azure.mgmt.migrationassessment.operations.AssessedSqlMachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                assessed_sql_machine_name: str, 
                **kwargs: Any
            ) -> AssessedSqlMachine: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AssessedSqlMachine]: ...


    class azure.mgmt.migrationassessment.operations.AssessedSqlRecommendedEntityOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                recommended_assessed_entity_name: str, 
                **kwargs: Any
            ) -> AssessedSqlRecommendedEntity: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AssessedSqlRecommendedEntity]: ...


    class azure.mgmt.migrationassessment.operations.AssessmentOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_options_name: str, 
                **kwargs: Any
            ) -> AssessmentOptions: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[AssessmentOptions]: ...


    class azure.mgmt.migrationassessment.operations.AssessmentProjectSummaryOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                project_summary_name: str, 
                **kwargs: Any
            ) -> AssessmentProjectSummary: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[AssessmentProjectSummary]: ...


    class azure.mgmt.migrationassessment.operations.AssessmentProjectsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                resource: AssessmentProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssessmentProject]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssessmentProject]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                properties: AssessmentProjectUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssessmentProject]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssessmentProject]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AssessmentProject: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[AssessmentProject]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[AssessmentProject]: ...


    class azure.mgmt.migrationassessment.operations.AssessmentsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: Assessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Assessment]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Assessment]: ...

        @distributed_trace
        def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> LROPoller[DownloadUrl]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> Assessment: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> Iterable[Assessment]: ...


    class azure.mgmt.migrationassessment.operations.AvsAssessedMachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                avs_assessed_machine_name: str, 
                **kwargs: Any
            ) -> AvsAssessedMachine: ...

        @distributed_trace
        def list_by_avs_assessment(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AvsAssessedMachine]: ...


    class azure.mgmt.migrationassessment.operations.AvsAssessmentOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                avs_assessment_options_name: str, 
                **kwargs: Any
            ) -> AvsAssessmentOptions: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[AvsAssessmentOptions]: ...


    class azure.mgmt.migrationassessment.operations.AvsAssessmentsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: AvsAssessment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsAssessment]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvsAssessment]: ...

        @distributed_trace
        def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> LROPoller[DownloadUrl]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> AvsAssessment: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> Iterable[AvsAssessment]: ...


    class azure.mgmt.migrationassessment.operations.GroupsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                resource: Group, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Group]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Group]: ...

        @overload
        def begin_update_machines(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                body: UpdateGroupBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Group]: ...

        @overload
        def begin_update_machines(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Group]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> Group: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[Group]: ...


    class azure.mgmt.migrationassessment.operations.HypervCollectorsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                hyperv_collector_name: str, 
                resource: HypervCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HypervCollector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                hyperv_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HypervCollector]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                hyperv_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                hyperv_collector_name: str, 
                **kwargs: Any
            ) -> HypervCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[HypervCollector]: ...


    class azure.mgmt.migrationassessment.operations.ImportCollectorsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                import_collector_name: str, 
                resource: ImportCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportCollector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                import_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportCollector]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                import_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                import_collector_name: str, 
                **kwargs: Any
            ) -> ImportCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[ImportCollector]: ...


    class azure.mgmt.migrationassessment.operations.MachinesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> Machine: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                continuation_token_parameter: Optional[str] = None, 
                total_record_count: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Machine]: ...


    class azure.mgmt.migrationassessment.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.migrationassessment.operations.PrivateEndpointConnectionOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnection]: ...


    class azure.mgmt.migrationassessment.operations.PrivateLinkResourceOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


    class azure.mgmt.migrationassessment.operations.ServerCollectorsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                server_collector_name: str, 
                resource: ServerCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerCollector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                server_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServerCollector]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                server_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                server_collector_name: str, 
                **kwargs: Any
            ) -> ServerCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[ServerCollector]: ...


    class azure.mgmt.migrationassessment.operations.SqlAssessmentOptionsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                assessment_options_name: str, 
                **kwargs: Any
            ) -> SqlAssessmentOptions: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[SqlAssessmentOptions]: ...


    class azure.mgmt.migrationassessment.operations.SqlAssessmentV2OperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: SqlAssessmentV2, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlAssessmentV2]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlAssessmentV2]: ...

        @distributed_trace
        def begin_download_url(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> LROPoller[DownloadUrl]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> SqlAssessmentV2: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> Iterable[SqlAssessmentV2]: ...


    class azure.mgmt.migrationassessment.operations.SqlAssessmentV2SummaryOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                summary_name: str, 
                **kwargs: Any
            ) -> SqlAssessmentV2Summary: ...

        @distributed_trace
        def list_by_sql_assessment_v2(
                self, 
                resource_group_name: str, 
                project_name: str, 
                group_name: str, 
                assessment_name: str, 
                **kwargs: Any
            ) -> Iterable[SqlAssessmentV2Summary]: ...


    class azure.mgmt.migrationassessment.operations.SqlCollectorOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                collector_name: str, 
                resource: SqlCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlCollector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlCollector]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                collector_name: str, 
                **kwargs: Any
            ) -> SqlCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[SqlCollector]: ...


    class azure.mgmt.migrationassessment.operations.VmwareCollectorsOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                vm_ware_collector_name: str, 
                resource: VmwareCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmwareCollector]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                vm_ware_collector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VmwareCollector]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                vm_ware_collector_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                vm_ware_collector_name: str, 
                **kwargs: Any
            ) -> VmwareCollector: ...

        @distributed_trace
        def list_by_assessment_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Iterable[VmwareCollector]: ...


```