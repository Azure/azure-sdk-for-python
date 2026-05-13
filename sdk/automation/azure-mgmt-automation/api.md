```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.automation

    class azure.mgmt.automation.AutomationClient(AutomationClientOperationsMixin): implements ContextManager 
        activity: ActivityOperations
        agent_registration_information: AgentRegistrationInformationOperations
        automation_account: AutomationAccountOperations
        certificate: CertificateOperations
        connection: ConnectionOperations
        connection_type: ConnectionTypeOperations
        credential: CredentialOperations
        deleted_automation_accounts: DeletedAutomationAccountsOperations
        dsc_compilation_job: DscCompilationJobOperations
        dsc_compilation_job_stream: DscCompilationJobStreamOperations
        dsc_configuration: DscConfigurationOperations
        dsc_node: DscNodeOperations
        dsc_node_configuration: DscNodeConfigurationOperations
        fields: FieldsOperations
        hybrid_runbook_worker_group: HybridRunbookWorkerGroupOperations
        hybrid_runbook_workers: HybridRunbookWorkersOperations
        job: JobOperations
        job_schedule: JobScheduleOperations
        job_stream: JobStreamOperations
        keys: KeysOperations
        linked_workspace: LinkedWorkspaceOperations
        module: ModuleOperations
        node_count_information: NodeCountInformationOperations
        node_reports: NodeReportsOperations
        object_data_types: ObjectDataTypesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        python2_package: Python2PackageOperations
        python3_package: Python3PackageOperations
        runbook: RunbookOperations
        runbook_draft: RunbookDraftOperations
        schedule: ScheduleOperations
        software_update_configuration_machine_runs: SoftwareUpdateConfigurationMachineRunsOperations
        software_update_configuration_runs: SoftwareUpdateConfigurationRunsOperations
        software_update_configurations: SoftwareUpdateConfigurationsOperations
        source_control: SourceControlOperations
        source_control_sync_job: SourceControlSyncJobOperations
        source_control_sync_job_streams: SourceControlSyncJobStreamsOperations
        statistics: StatisticsOperations
        test_job: TestJobOperations
        test_job_streams: TestJobStreamsOperations
        usages: UsagesOperations
        variable: VariableOperations
        watcher: WatcherOperations
        webhook: WebhookOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: GraphicalRunbookContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...

        @overload
        def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...


namespace azure.mgmt.automation.aio

    class azure.mgmt.automation.aio.AutomationClient(AutomationClientOperationsMixin): implements AsyncContextManager 
        activity: ActivityOperations
        agent_registration_information: AgentRegistrationInformationOperations
        automation_account: AutomationAccountOperations
        certificate: CertificateOperations
        connection: ConnectionOperations
        connection_type: ConnectionTypeOperations
        credential: CredentialOperations
        deleted_automation_accounts: DeletedAutomationAccountsOperations
        dsc_compilation_job: DscCompilationJobOperations
        dsc_compilation_job_stream: DscCompilationJobStreamOperations
        dsc_configuration: DscConfigurationOperations
        dsc_node: DscNodeOperations
        dsc_node_configuration: DscNodeConfigurationOperations
        fields: FieldsOperations
        hybrid_runbook_worker_group: HybridRunbookWorkerGroupOperations
        hybrid_runbook_workers: HybridRunbookWorkersOperations
        job: JobOperations
        job_schedule: JobScheduleOperations
        job_stream: JobStreamOperations
        keys: KeysOperations
        linked_workspace: LinkedWorkspaceOperations
        module: ModuleOperations
        node_count_information: NodeCountInformationOperations
        node_reports: NodeReportsOperations
        object_data_types: ObjectDataTypesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        python2_package: Python2PackageOperations
        python3_package: Python3PackageOperations
        runbook: RunbookOperations
        runbook_draft: RunbookDraftOperations
        schedule: ScheduleOperations
        software_update_configuration_machine_runs: SoftwareUpdateConfigurationMachineRunsOperations
        software_update_configuration_runs: SoftwareUpdateConfigurationRunsOperations
        software_update_configurations: SoftwareUpdateConfigurationsOperations
        source_control: SourceControlOperations
        source_control_sync_job: SourceControlSyncJobOperations
        source_control_sync_job_streams: SourceControlSyncJobStreamsOperations
        statistics: StatisticsOperations
        test_job: TestJobOperations
        test_job_streams: TestJobStreamsOperations
        usages: UsagesOperations
        variable: VariableOperations
        watcher: WatcherOperations
        webhook: WebhookOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: GraphicalRunbookContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...

        @overload
        async def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...


namespace azure.mgmt.automation.aio.operations

    class azure.mgmt.automation.aio.operations.ActivityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                activity_name: str, 
                **kwargs: Any
            ) -> Activity: ...

        @distributed_trace
        def list_by_module(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Activity]: ...


    class azure.mgmt.automation.aio.operations.AgentRegistrationInformationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AgentRegistration: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: AgentRegistrationRegenerateKeyParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentRegistration: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentRegistration: ...


    class azure.mgmt.automation.aio.operations.AutomationAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: AutomationAccountCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[AutomationAccount]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AutomationAccount]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: AutomationAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...


    class azure.mgmt.automation.aio.operations.AutomationClientOperationsMixin(AutomationClientMixinABC):

        @overload
        async def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: GraphicalRunbookContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...

        @overload
        async def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...


    class azure.mgmt.automation.aio.operations.CertificateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: CertificateCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Certificate]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: CertificateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...


    class azure.mgmt.automation.aio.operations.ConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: ConnectionCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Connection]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: ConnectionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...


    class azure.mgmt.automation.aio.operations.ConnectionTypeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                parameters: ConnectionTypeCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionType: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionType: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                **kwargs: Any
            ) -> ConnectionType: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ConnectionType]: ...


    class azure.mgmt.automation.aio.operations.CredentialOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: CredentialCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                **kwargs: Any
            ) -> Credential: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Credential]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: CredentialUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...


    class azure.mgmt.automation.aio.operations.DeletedAutomationAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_subscription(self, **kwargs: Any) -> DeletedAutomationAccountListResult: ...


    class azure.mgmt.automation.aio.operations.DscCompilationJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                compilation_job_name: str, 
                parameters: DscCompilationJobCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DscCompilationJob]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                compilation_job_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DscCompilationJob]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                compilation_job_name: str, 
                **kwargs: Any
            ) -> DscCompilationJob: ...

        @distributed_trace_async
        async def get_stream(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_id: str, 
                job_stream_id: str, 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DscCompilationJob]: ...


    class azure.mgmt.automation.aio.operations.DscCompilationJobStreamOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> JobStreamListResult: ...


    class azure.mgmt.automation.aio.operations.DscConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: DscConfigurationCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: str, 
                *, 
                content_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @distributed_trace_async
        async def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                inlinecount: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DscConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: Optional[DscConfigurationUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: Optional[str] = None, 
                *, 
                content_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> DscConfiguration: ...


    class azure.mgmt.automation.aio.operations.DscNodeConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                parameters: DscNodeConfigurationCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DscNodeConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DscNodeConfiguration]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                **kwargs: Any
            ) -> DscNodeConfiguration: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                inlinecount: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DscNodeConfiguration]: ...


    class azure.mgmt.automation.aio.operations.DscNodeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                **kwargs: Any
            ) -> DscNode: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                inlinecount: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DscNode]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                dsc_node_update_parameters: DscNodeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscNode: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                dsc_node_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscNode: ...


    class azure.mgmt.automation.aio.operations.FieldsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[TypeField]: ...


    class azure.mgmt.automation.aio.operations.HybridRunbookWorkerGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_creation_parameters: HybridRunbookWorkerGroupCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_creation_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[HybridRunbookWorkerGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_updation_parameters: HybridRunbookWorkerGroupCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_updation_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...


    class azure.mgmt.automation.aio.operations.HybridRunbookWorkersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: HybridRunbookWorkerCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @distributed_trace
        def list_by_hybrid_runbook_worker_group(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[HybridRunbookWorker]: ...

        @overload
        async def move(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_move_parameters: HybridRunbookWorkerMoveParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def move(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_move_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.automation.aio.operations.JobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                parameters: JobCreateParameters, 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                parameters: IO[bytes], 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace_async
        async def get_output(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace_async
        async def get_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[JobCollectionItem]: ...

        @distributed_trace_async
        async def resume(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def suspend(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.automation.aio.operations.JobScheduleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                parameters: JobScheduleCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobSchedule: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobSchedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                **kwargs: Any
            ) -> JobSchedule: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[JobSchedule]: ...


    class azure.mgmt.automation.aio.operations.JobStreamOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                job_stream_id: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                filter: Optional[str] = None, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[JobStream]: ...


    class azure.mgmt.automation.aio.operations.KeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> KeyListResult: ...


    class azure.mgmt.automation.aio.operations.LinkedWorkspaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> LinkedWorkspace: ...


    class azure.mgmt.automation.aio.operations.ModuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: ModuleCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Module]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: ModuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...


    class azure.mgmt.automation.aio.operations.NodeCountInformationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                count_type: Union[str, CountType], 
                **kwargs: Any
            ) -> NodeCounts: ...


    class azure.mgmt.automation.aio.operations.NodeReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                report_id: str, 
                **kwargs: Any
            ) -> DscNodeReport: ...

        @distributed_trace_async
        async def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                report_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_by_node(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DscNodeReport]: ...


    class azure.mgmt.automation.aio.operations.ObjectDataTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_fields_by_module_and_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[TypeField]: ...

        @distributed_trace
        def list_fields_by_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[TypeField]: ...


    class azure.mgmt.automation.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.automation.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnection]: ...


    class azure.mgmt.automation.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def automation(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


    class azure.mgmt.automation.aio.operations.Python2PackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Module]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...


    class azure.mgmt.automation.aio.operations.Python3PackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Module]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...


    class azure.mgmt.automation.aio.operations.RunbookDraftOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_replace_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                runbook_content: IO[bytes], 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncIterator[bytes]]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> RunbookDraft: ...

        @distributed_trace_async
        async def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def undo_edit(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> RunbookDraftUndoEditResult: ...


    class azure.mgmt.automation.aio.operations.RunbookOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_publish(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: RunbookCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> Runbook: ...

        @distributed_trace_async
        async def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Runbook]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: RunbookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...


    class azure.mgmt.automation.aio.operations.ScheduleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: ScheduleCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[Schedule]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[Schedule]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: ScheduleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.automation.aio.operations.SoftwareUpdateConfigurationMachineRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_machine_run_id: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationMachineRun: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                client_request_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationMachineRunListResult: ...


    class azure.mgmt.automation.aio.operations.SoftwareUpdateConfigurationRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_id(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_run_id: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationRun: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                client_request_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationRunListResult: ...


    class azure.mgmt.automation.aio.operations.SoftwareUpdateConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                parameters: SoftwareUpdateConfiguration, 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                parameters: IO[bytes], 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_name(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                client_request_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationListResult: ...


    class azure.mgmt.automation.aio.operations.SourceControlOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: SourceControlCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SourceControl]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: SourceControlUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...


    class azure.mgmt.automation.aio.operations.SourceControlSyncJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                parameters: SourceControlSyncJobCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControlSyncJob: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControlSyncJob: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                **kwargs: Any
            ) -> SourceControlSyncJobById: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SourceControlSyncJob]: ...


    class azure.mgmt.automation.aio.operations.SourceControlSyncJobStreamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                stream_id: str, 
                **kwargs: Any
            ) -> SourceControlSyncJobStreamById: ...

        @distributed_trace
        def list_by_sync_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SourceControlSyncJobStream]: ...


    class azure.mgmt.automation.aio.operations.StatisticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Statistics]: ...


    class azure.mgmt.automation.aio.operations.TestJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: TestJobCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestJob: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestJob: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> TestJob: ...

        @distributed_trace_async
        async def resume(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def suspend(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.automation.aio.operations.TestJobStreamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                job_stream_id: str, 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_test_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[JobStream]: ...


    class azure.mgmt.automation.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


    class azure.mgmt.automation.aio.operations.VariableOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: VariableCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Variable]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: VariableUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...


    class azure.mgmt.automation.aio.operations.WatcherOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: Watcher, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Watcher: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Watcher]: ...

        @distributed_trace_async
        async def start(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: WatcherUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...


    class azure.mgmt.automation.aio.operations.WebhookOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: WebhookCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def generate_uri(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> Webhook: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Webhook]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: WebhookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...


namespace azure.mgmt.automation.models

    class azure.mgmt.automation.models.Activity(Model):
        creation_time: datetime
        definition: str
        description: str
        id: str
        last_modified_time: datetime
        name: str
        output_types: list[ActivityOutputType]
        parameter_sets: list[ActivityParameterSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                definition: Optional[str] = ..., 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                output_types: Optional[List[ActivityOutputType]] = ..., 
                parameter_sets: Optional[List[ActivityParameterSet]] = ..., 
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


    class azure.mgmt.automation.models.ActivityListResult(Model):
        next_link: str
        value: list[Activity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Activity]] = ..., 
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


    class azure.mgmt.automation.models.ActivityOutputType(Model):
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


    class azure.mgmt.automation.models.ActivityParameter(Model):
        description: str
        is_dynamic: bool
        is_mandatory: bool
        name: str
        position: int
        type: str
        validation_set: list[ActivityParameterValidationSet]
        value_from_pipeline: bool
        value_from_pipeline_by_property_name: bool
        value_from_remaining_arguments: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_dynamic: Optional[bool] = ..., 
                is_mandatory: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                position: Optional[int] = ..., 
                type: Optional[str] = ..., 
                validation_set: Optional[List[ActivityParameterValidationSet]] = ..., 
                value_from_pipeline: Optional[bool] = ..., 
                value_from_pipeline_by_property_name: Optional[bool] = ..., 
                value_from_remaining_arguments: Optional[bool] = ..., 
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


    class azure.mgmt.automation.models.ActivityParameterSet(Model):
        name: str
        parameters: list[ActivityParameter]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[List[ActivityParameter]] = ..., 
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


    class azure.mgmt.automation.models.ActivityParameterValidationSet(Model):
        member_value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                member_value: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.AdvancedSchedule(Model):
        month_days: list[int]
        monthly_occurrences: list[AdvancedScheduleMonthlyOccurrence]
        week_days: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                month_days: Optional[List[int]] = ..., 
                monthly_occurrences: Optional[List[AdvancedScheduleMonthlyOccurrence]] = ..., 
                week_days: Optional[List[str]] = ..., 
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


    class azure.mgmt.automation.models.AdvancedScheduleMonthlyOccurrence(Model):
        day: Union[str, ScheduleDay]
        occurrence: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                day: Optional[Union[str, ScheduleDay]] = ..., 
                occurrence: Optional[int] = ..., 
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


    class azure.mgmt.automation.models.AgentRegistration(Model):
        dsc_meta_configuration: str
        endpoint: str
        id: str
        keys: AgentRegistrationKeys

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dsc_meta_configuration: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                id: Optional[str] = ..., 
                keys: Optional[AgentRegistrationKeys] = ..., 
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


    class azure.mgmt.automation.models.AgentRegistrationKeyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "primary"
        SECONDARY = "secondary"


    class azure.mgmt.automation.models.AgentRegistrationKeys(Model):
        primary: str
        secondary: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                primary: Optional[str] = ..., 
                secondary: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.AgentRegistrationRegenerateKeyParameter(Model):
        key_name: Union[str, AgentRegistrationKeyName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: Union[str, AgentRegistrationKeyName], 
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


    class azure.mgmt.automation.models.AutomationAccount(TrackedResource):
        automation_hybrid_service_url: str
        creation_time: datetime
        description: str
        disable_local_auth: bool
        encryption: EncryptionProperties
        etag: str
        id: str
        identity: Identity
        last_modified_by: str
        last_modified_time: datetime
        location: str
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        public_network_access: bool
        sku: Sku
        state: Union[str, AutomationAccountState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                automation_hybrid_service_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                etag: Optional[str] = ..., 
                identity: Optional[Identity] = ..., 
                last_modified_by: Optional[str] = ..., 
                location: Optional[str] = ..., 
                private_endpoint_connections: Optional[List[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[bool] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.automation.models.AutomationAccountCreateOrUpdateParameters(Model):
        disable_local_auth: bool
        encryption: EncryptionProperties
        identity: Identity
        location: str
        name: str
        public_network_access: bool
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                public_network_access: Optional[bool] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.automation.models.AutomationAccountListResult(Model):
        next_link: str
        value: list[AutomationAccount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AutomationAccount]] = ..., 
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


    class azure.mgmt.automation.models.AutomationAccountState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OK = "Ok"
        SUSPENDED = "Suspended"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.automation.models.AutomationAccountUpdateParameters(Model):
        disable_local_auth: bool
        encryption: EncryptionProperties
        identity: Identity
        location: str
        name: str
        public_network_access: bool
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                public_network_access: Optional[bool] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.automation.models.AutomationKeyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.automation.models.AutomationKeyPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        READ = "Read"


    class azure.mgmt.automation.models.AzureQueryProperties(Model):
        locations: list[str]
        scope: list[str]
        tag_settings: TagSettingsProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                locations: Optional[List[str]] = ..., 
                scope: Optional[List[str]] = ..., 
                tag_settings: Optional[TagSettingsProperties] = ..., 
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


    class azure.mgmt.automation.models.Certificate(ProxyResource):
        creation_time: datetime
        description: str
        expiry_time: datetime
        id: str
        is_exportable: bool
        last_modified_time: datetime
        name: str
        thumbprint: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.CertificateCreateOrUpdateParameters(Model):
        base64_value: str
        description: str
        is_exportable: bool
        name: str
        thumbprint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                base64_value: str, 
                description: Optional[str] = ..., 
                is_exportable: Optional[bool] = ..., 
                name: str, 
                thumbprint: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.CertificateListResult(Model):
        next_link: str
        value: list[Certificate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Certificate]] = ..., 
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


    class azure.mgmt.automation.models.CertificateUpdateParameters(Model):
        description: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.Connection(ProxyResource):
        connection_type: ConnectionTypeAssociationProperty
        creation_time: datetime
        description: str
        field_definition_values: dict[str, str]
        id: str
        last_modified_time: datetime
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_type: Optional[ConnectionTypeAssociationProperty] = ..., 
                description: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ConnectionCreateOrUpdateParameters(Model):
        connection_type: ConnectionTypeAssociationProperty
        description: str
        field_definition_values: dict[str, str]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_type: ConnectionTypeAssociationProperty, 
                description: Optional[str] = ..., 
                field_definition_values: Optional[Dict[str, str]] = ..., 
                name: str, 
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


    class azure.mgmt.automation.models.ConnectionListResult(Model):
        next_link: str
        value: list[Connection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Connection]] = ..., 
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


    class azure.mgmt.automation.models.ConnectionType(Model):
        creation_time: datetime
        description: str
        field_definitions: dict[str, FieldDefinition]
        id: str
        is_global: bool
        last_modified_time: datetime
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_global: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
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


    class azure.mgmt.automation.models.ConnectionTypeAssociationProperty(Model):
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


    class azure.mgmt.automation.models.ConnectionTypeCreateOrUpdateParameters(Model):
        field_definitions: dict[str, FieldDefinition]
        is_global: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                field_definitions: Dict[str, FieldDefinition], 
                is_global: Optional[bool] = ..., 
                name: str, 
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


    class azure.mgmt.automation.models.ConnectionTypeListResult(Model):
        next_link: str
        value: list[ConnectionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ConnectionType]] = ..., 
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


    class azure.mgmt.automation.models.ConnectionUpdateParameters(Model):
        description: str
        field_definition_values: dict[str, str]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                field_definition_values: Optional[Dict[str, str]] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ContentHash(Model):
        algorithm: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                algorithm: str, 
                value: str, 
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


    class azure.mgmt.automation.models.ContentLink(Model):
        content_hash: ContentHash
        uri: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_hash: Optional[ContentHash] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ContentSource(Model):
        hash: ContentHash
        type: Union[str, ContentSourceType]
        value: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hash: Optional[ContentHash] = ..., 
                type: Optional[Union[str, ContentSourceType]] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ContentSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMBEDDED_CONTENT = "embeddedContent"
        URI = "uri"


    class azure.mgmt.automation.models.CountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NODECONFIGURATION = "nodeconfiguration"
        STATUS = "status"


    class azure.mgmt.automation.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.automation.models.Credential(ProxyResource):
        creation_time: datetime
        description: str
        id: str
        last_modified_time: datetime
        name: str
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.CredentialCreateOrUpdateParameters(Model):
        description: str
        name: str
        password: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                password: str, 
                user_name: str, 
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


    class azure.mgmt.automation.models.CredentialListResult(Model):
        next_link: str
        value: list[Credential]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Credential]] = ..., 
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


    class azure.mgmt.automation.models.CredentialUpdateParameters(Model):
        description: str
        name: str
        password: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                user_name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DeletedAutomationAccount(Model):
        automation_account_id: str
        automation_account_resource_id: str
        deletion_time: datetime
        id: str
        location: str
        location_properties_location: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                automation_account_id: Optional[str] = ..., 
                automation_account_resource_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                location_properties_location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DeletedAutomationAccountListResult(Model):
        value: list[DeletedAutomationAccount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[DeletedAutomationAccount]] = ..., 
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


    class azure.mgmt.automation.models.Dimension(Model):
        display_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscCompilationJob(ProxyResource):
        configuration: DscConfigurationAssociationProperty
        creation_time: datetime
        end_time: datetime
        exception: str
        id: str
        job_id: str
        last_modified_time: datetime
        last_status_modified_time: datetime
        name: str
        parameters: dict[str, str]
        provisioning_state: Union[str, JobProvisioningState]
        run_on: str
        start_time: datetime
        started_by: str
        status: Union[str, JobStatus]
        status_details: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[DscConfigurationAssociationProperty] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                provisioning_state: Optional[Union[str, JobProvisioningState]] = ..., 
                run_on: Optional[str] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                status_details: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscCompilationJobCreateParameters(Model):
        configuration: DscConfigurationAssociationProperty
        increment_node_configuration_build: bool
        location: str
        name: str
        parameters: dict[str, str]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: DscConfigurationAssociationProperty, 
                increment_node_configuration_build: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.automation.models.DscCompilationJobListResult(Model):
        next_link: str
        value: list[DscCompilationJob]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DscCompilationJob]] = ..., 
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


    class azure.mgmt.automation.models.DscConfiguration(TrackedResource):
        creation_time: datetime
        description: str
        etag: str
        id: str
        job_count: int
        last_modified_time: datetime
        location: str
        log_verbose: bool
        name: str
        node_configuration_count: int
        parameters: dict[str, DscConfigurationParameter]
        provisioning_state: str
        source: ContentSource
        state: Union[str, DscConfigurationState]
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                job_count: Optional[int] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                location: Optional[str] = ..., 
                log_verbose: Optional[bool] = ..., 
                node_configuration_count: Optional[int] = ..., 
                parameters: Optional[Dict[str, DscConfigurationParameter]] = ..., 
                provisioning_state: Optional[Literal[Succeeded]] = ..., 
                source: Optional[ContentSource] = ..., 
                state: Optional[Union[str, DscConfigurationState]] = ..., 
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


    class azure.mgmt.automation.models.DscConfigurationAssociationProperty(Model):
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


    class azure.mgmt.automation.models.DscConfigurationCreateOrUpdateParameters(Model):
        description: str
        location: str
        log_progress: bool
        log_verbose: bool
        name: str
        parameters: dict[str, DscConfigurationParameter]
        source: ContentSource
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                location: Optional[str] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[Dict[str, DscConfigurationParameter]] = ..., 
                source: ContentSource, 
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


    class azure.mgmt.automation.models.DscConfigurationListResult(Model):
        next_link: str
        total_count: int
        value: list[DscConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                total_count: Optional[int] = ..., 
                value: Optional[List[DscConfiguration]] = ..., 
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


    class azure.mgmt.automation.models.DscConfigurationParameter(Model):
        default_value: str
        is_mandatory: bool
        position: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                is_mandatory: Optional[bool] = ..., 
                position: Optional[int] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDIT = "Edit"
        NEW = "New"
        PUBLISHED = "Published"


    class azure.mgmt.automation.models.DscConfigurationUpdateParameters(Model):
        description: str
        log_progress: bool
        log_verbose: bool
        name: str
        parameters: dict[str, DscConfigurationParameter]
        source: ContentSource
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[Dict[str, DscConfigurationParameter]] = ..., 
                source: Optional[ContentSource] = ..., 
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


    class azure.mgmt.automation.models.DscMetaConfiguration(Model):
        action_after_reboot: str
        allow_module_overwrite: bool
        certificate_id: str
        configuration_mode: str
        configuration_mode_frequency_mins: int
        reboot_node_if_needed: bool
        refresh_frequency_mins: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_after_reboot: Optional[str] = ..., 
                allow_module_overwrite: Optional[bool] = ..., 
                certificate_id: Optional[str] = ..., 
                configuration_mode: Optional[str] = ..., 
                configuration_mode_frequency_mins: Optional[int] = ..., 
                reboot_node_if_needed: Optional[bool] = ..., 
                refresh_frequency_mins: Optional[int] = ..., 
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


    class azure.mgmt.automation.models.DscNode(ProxyResource):
        account_id: str
        etag: str
        extension_handler: list[DscNodeExtensionHandlerAssociationProperty]
        id: str
        ip: str
        last_seen: datetime
        name: str
        name_properties_node_configuration_name: str
        node_id: str
        registration_time: datetime
        status: str
        total_count: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                extension_handler: Optional[List[DscNodeExtensionHandlerAssociationProperty]] = ..., 
                ip: Optional[str] = ..., 
                last_seen: Optional[datetime] = ..., 
                name_properties_node_configuration_name: Optional[str] = ..., 
                node_id: Optional[str] = ..., 
                registration_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                total_count: Optional[int] = ..., 
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


    class azure.mgmt.automation.models.DscNodeConfiguration(ProxyResource):
        configuration: DscConfigurationAssociationProperty
        creation_time: datetime
        id: str
        increment_node_configuration_build: bool
        last_modified_time: datetime
        name: str
        node_count: int
        source: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[DscConfigurationAssociationProperty] = ..., 
                creation_time: Optional[datetime] = ..., 
                increment_node_configuration_build: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                node_count: Optional[int] = ..., 
                source: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscNodeConfigurationCreateOrUpdateParameters(Model):
        configuration: DscConfigurationAssociationProperty
        increment_node_configuration_build: bool
        name: str
        source: ContentSource
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[DscConfigurationAssociationProperty] = ..., 
                increment_node_configuration_build: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                source: Optional[ContentSource] = ..., 
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


    class azure.mgmt.automation.models.DscNodeConfigurationListResult(Model):
        next_link: str
        total_count: int
        value: list[DscNodeConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                total_count: Optional[int] = ..., 
                value: Optional[List[DscNodeConfiguration]] = ..., 
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


    class azure.mgmt.automation.models.DscNodeExtensionHandlerAssociationProperty(Model):
        name: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscNodeListResult(Model):
        next_link: str
        total_count: int
        value: list[DscNode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                total_count: Optional[int] = ..., 
                value: Optional[List[DscNode]] = ..., 
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


    class azure.mgmt.automation.models.DscNodeReport(Model):
        configuration_version: str
        end_time: datetime
        errors: list[DscReportError]
        host_name: str
        i_pv4_addresses: list[str]
        i_pv6_addresses: list[str]
        id: str
        last_modified_time: datetime
        meta_configuration: DscMetaConfiguration
        number_of_resources: int
        raw_errors: str
        reboot_requested: str
        refresh_mode: str
        report_format_version: str
        report_id: str
        resources: list[DscReportResource]
        start_time: datetime
        status: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_version: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                errors: Optional[List[DscReportError]] = ..., 
                host_name: Optional[str] = ..., 
                i_pv4_addresses: Optional[List[str]] = ..., 
                i_pv6_addresses: Optional[List[str]] = ..., 
                id: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                meta_configuration: Optional[DscMetaConfiguration] = ..., 
                number_of_resources: Optional[int] = ..., 
                raw_errors: Optional[str] = ..., 
                reboot_requested: Optional[str] = ..., 
                refresh_mode: Optional[str] = ..., 
                report_format_version: Optional[str] = ..., 
                report_id: Optional[str] = ..., 
                resources: Optional[List[DscReportResource]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscNodeReportListResult(Model):
        next_link: str
        value: list[DscNodeReport]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DscNodeReport]] = ..., 
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


    class azure.mgmt.automation.models.DscNodeUpdateParameters(Model):
        node_id: str
        properties: DscNodeUpdateParametersProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                node_id: Optional[str] = ..., 
                properties: Optional[DscNodeUpdateParametersProperties] = ..., 
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


    class azure.mgmt.automation.models.DscNodeUpdateParametersProperties(Model):
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


    class azure.mgmt.automation.models.DscReportError(Model):
        error_code: str
        error_details: str
        error_message: str
        error_source: str
        locale: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_details: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                error_source: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscReportResource(Model):
        depends_on: list[DscReportResourceNavigation]
        duration_in_seconds: float
        error: str
        module_name: str
        module_version: str
        resource_id: str
        resource_name: str
        source_info: str
        start_date: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on: Optional[List[DscReportResourceNavigation]] = ..., 
                duration_in_seconds: Optional[float] = ..., 
                error: Optional[str] = ..., 
                module_name: Optional[str] = ..., 
                module_version: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                source_info: Optional[str] = ..., 
                start_date: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.DscReportResourceNavigation(Model):
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.EncryptionKeySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_AUTOMATION = "Microsoft.Automation"
        MICROSOFT_KEYVAULT = "Microsoft.Keyvault"


    class azure.mgmt.automation.models.EncryptionProperties(Model):
        identity: EncryptionPropertiesIdentity
        key_source: Union[str, EncryptionKeySourceType]
        key_vault_properties: KeyVaultProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[EncryptionPropertiesIdentity] = ..., 
                key_source: Optional[Union[str, EncryptionKeySourceType]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
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


    class azure.mgmt.automation.models.EncryptionPropertiesIdentity(Model):
        user_assigned_identity: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                user_assigned_identity: Optional[JSON] = ..., 
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


    class azure.mgmt.automation.models.ErrorResponse(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.FieldDefinition(Model):
        is_encrypted: bool
        is_optional: bool
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_encrypted: Optional[bool] = ..., 
                is_optional: Optional[bool] = ..., 
                type: str, 
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


    class azure.mgmt.automation.models.GraphRunbookType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAPH_POWER_SHELL = "GraphPowerShell"
        GRAPH_POWER_SHELL_WORKFLOW = "GraphPowerShellWorkflow"


    class azure.mgmt.automation.models.GraphicalRunbookContent(Model):
        graph_runbook_json: str
        raw_content: RawGraphicalRunbookContent

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                graph_runbook_json: Optional[str] = ..., 
                raw_content: Optional[RawGraphicalRunbookContent] = ..., 
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


    class azure.mgmt.automation.models.GroupTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.automation.models.HttpStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        AMBIGUOUS = "Ambiguous"
        BAD_GATEWAY = "BadGateway"
        BAD_REQUEST = "BadRequest"
        CONFLICT = "Conflict"
        CONTINUE = "Continue"
        CONTINUE_ENUM = "Continue"
        CREATED = "Created"
        EXPECTATION_FAILED = "ExpectationFailed"
        FORBIDDEN = "Forbidden"
        FOUND = "Found"
        GATEWAY_TIMEOUT = "GatewayTimeout"
        GONE = "Gone"
        HTTP_VERSION_NOT_SUPPORTED = "HttpVersionNotSupported"
        INTERNAL_SERVER_ERROR = "InternalServerError"
        LENGTH_REQUIRED = "LengthRequired"
        METHOD_NOT_ALLOWED = "MethodNotAllowed"
        MOVED = "Moved"
        MOVED_PERMANENTLY = "MovedPermanently"
        MULTIPLE_CHOICES = "MultipleChoices"
        NON_AUTHORITATIVE_INFORMATION = "NonAuthoritativeInformation"
        NOT_ACCEPTABLE = "NotAcceptable"
        NOT_FOUND = "NotFound"
        NOT_IMPLEMENTED = "NotImplemented"
        NOT_MODIFIED = "NotModified"
        NO_CONTENT = "NoContent"
        OK = "OK"
        PARTIAL_CONTENT = "PartialContent"
        PAYMENT_REQUIRED = "PaymentRequired"
        PRECONDITION_FAILED = "PreconditionFailed"
        PROXY_AUTHENTICATION_REQUIRED = "ProxyAuthenticationRequired"
        REDIRECT = "Redirect"
        REDIRECT_KEEP_VERB = "RedirectKeepVerb"
        REDIRECT_METHOD = "RedirectMethod"
        REQUESTED_RANGE_NOT_SATISFIABLE = "RequestedRangeNotSatisfiable"
        REQUEST_ENTITY_TOO_LARGE = "RequestEntityTooLarge"
        REQUEST_TIMEOUT = "RequestTimeout"
        REQUEST_URI_TOO_LONG = "RequestUriTooLong"
        RESET_CONTENT = "ResetContent"
        SEE_OTHER = "SeeOther"
        SERVICE_UNAVAILABLE = "ServiceUnavailable"
        SWITCHING_PROTOCOLS = "SwitchingProtocols"
        TEMPORARY_REDIRECT = "TemporaryRedirect"
        UNAUTHORIZED = "Unauthorized"
        UNSUPPORTED_MEDIA_TYPE = "UnsupportedMediaType"
        UNUSED = "Unused"
        UPGRADE_REQUIRED = "UpgradeRequired"
        USE_PROXY = "UseProxy"


    class azure.mgmt.automation.models.HybridRunbookWorker(Resource):
        id: str
        ip: str
        last_seen_date_time: datetime
        name: str
        registered_date_time: datetime
        system_data: SystemData
        type: str
        vm_resource_id: str
        worker_name: str
        worker_type: Union[str, WorkerType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip: Optional[str] = ..., 
                last_seen_date_time: Optional[datetime] = ..., 
                registered_date_time: Optional[datetime] = ..., 
                vm_resource_id: Optional[str] = ..., 
                worker_name: Optional[str] = ..., 
                worker_type: Optional[Union[str, WorkerType]] = ..., 
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


    class azure.mgmt.automation.models.HybridRunbookWorkerCreateParameters(Model):
        name: str
        vm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                vm_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.HybridRunbookWorkerGroup(Resource):
        credential: RunAsCredentialAssociationProperty
        group_type: Union[str, GroupTypeEnum]
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                credential: Optional[RunAsCredentialAssociationProperty] = ..., 
                group_type: Optional[Union[str, GroupTypeEnum]] = ..., 
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


    class azure.mgmt.automation.models.HybridRunbookWorkerGroupCreateOrUpdateParameters(Model):
        credential: RunAsCredentialAssociationProperty
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                credential: Optional[RunAsCredentialAssociationProperty] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.HybridRunbookWorkerGroupsListResult(Model):
        next_link: str
        value: list[HybridRunbookWorkerGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[HybridRunbookWorkerGroup]] = ..., 
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


    class azure.mgmt.automation.models.HybridRunbookWorkerMoveParameters(Model):
        hybrid_runbook_worker_group_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hybrid_runbook_worker_group_name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.HybridRunbookWorkersListResult(Model):
        next_link: str
        value: list[HybridRunbookWorker]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[HybridRunbookWorker]] = ..., 
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


    class azure.mgmt.automation.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentitiesProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentitiesProperties]] = ..., 
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


    class azure.mgmt.automation.models.Job(ProxyResource):
        creation_time: datetime
        end_time: datetime
        exception: str
        id: str
        job_id: str
        last_modified_time: datetime
        last_status_modified_time: datetime
        name: str
        parameters: dict[str, str]
        provisioning_state: Union[str, JobProvisioningState]
        run_on: str
        runbook: RunbookAssociationProperty
        start_time: datetime
        started_by: str
        status: Union[str, JobStatus]
        status_details: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                end_time: Optional[datetime] = ..., 
                exception: Optional[str] = ..., 
                job_id: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                last_status_modified_time: Optional[datetime] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                provisioning_state: Optional[Union[str, JobProvisioningState]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                start_time: Optional[datetime] = ..., 
                started_by: Optional[str] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                status_details: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.JobCollectionItem(ProxyResource):
        creation_time: datetime
        end_time: datetime
        id: str
        job_id: str
        last_modified_time: datetime
        name: str
        provisioning_state: str
        run_on: str
        runbook: RunbookAssociationProperty
        start_time: datetime
        status: Union[str, JobStatus]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                run_on: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.JobCreateParameters(Model):
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
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


    class azure.mgmt.automation.models.JobListResultV2(Model):
        next_link: str
        value: list[JobCollectionItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[JobCollectionItem]] = ..., 
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


    class azure.mgmt.automation.models.JobNavigation(Model):
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


    class azure.mgmt.automation.models.JobProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PROCESSING = "Processing"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"


    class azure.mgmt.automation.models.JobSchedule(Model):
        id: str
        job_schedule_id: str
        name: str
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty
        schedule: ScheduleAssociationProperty
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                job_schedule_id: Optional[str] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                schedule: Optional[ScheduleAssociationProperty] = ..., 
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


    class azure.mgmt.automation.models.JobScheduleCreateParameters(Model):
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty
        schedule: ScheduleAssociationProperty

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: RunbookAssociationProperty, 
                schedule: ScheduleAssociationProperty, 
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


    class azure.mgmt.automation.models.JobScheduleListResult(Model):
        next_link: str
        value: list[JobSchedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[JobSchedule]] = ..., 
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


    class azure.mgmt.automation.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATING = "Activating"
        BLOCKED = "Blocked"
        COMPLETED = "Completed"
        DISCONNECTED = "Disconnected"
        FAILED = "Failed"
        NEW = "New"
        REMOVING = "Removing"
        RESUMING = "Resuming"
        RUNNING = "Running"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        SUSPENDED = "Suspended"
        SUSPENDING = "Suspending"


    class azure.mgmt.automation.models.JobStream(Model):
        id: str
        job_stream_id: str
        stream_text: str
        stream_type: Union[str, JobStreamType]
        summary: str
        time: datetime
        value: dict[str, JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                job_stream_id: Optional[str] = ..., 
                stream_text: Optional[str] = ..., 
                stream_type: Optional[Union[str, JobStreamType]] = ..., 
                summary: Optional[str] = ..., 
                time: Optional[datetime] = ..., 
                value: Optional[Dict[str, JSON]] = ..., 
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


    class azure.mgmt.automation.models.JobStreamListResult(Model):
        next_link: str
        value: list[JobStream]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[JobStream]] = ..., 
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


    class azure.mgmt.automation.models.JobStreamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        DEBUG = "Debug"
        ERROR = "Error"
        OUTPUT = "Output"
        PROGRESS = "Progress"
        VERBOSE = "Verbose"
        WARNING = "Warning"


    class azure.mgmt.automation.models.Key(Model):
        key_name: Union[str, AutomationKeyName]
        permissions: Union[str, AutomationKeyPermissions]
        value: str

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


    class azure.mgmt.automation.models.KeyListResult(Model):
        keys: list[Key]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                keys: Optional[List[Key]] = ..., 
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


    class azure.mgmt.automation.models.KeyVaultProperties(Model):
        key_name: str
        key_version: str
        keyvault_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                keyvault_uri: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.LinkedWorkspace(Model):
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


    class azure.mgmt.automation.models.LinuxProperties(Model):
        excluded_package_name_masks: list[str]
        included_package_classifications: Union[str, LinuxUpdateClasses]
        included_package_name_masks: list[str]
        reboot_setting: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                excluded_package_name_masks: Optional[List[str]] = ..., 
                included_package_classifications: Optional[Union[str, LinuxUpdateClasses]] = ..., 
                included_package_name_masks: Optional[List[str]] = ..., 
                reboot_setting: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.LinuxUpdateClasses(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        OTHER = "Other"
        SECURITY = "Security"
        UNCLASSIFIED = "Unclassified"


    class azure.mgmt.automation.models.LogSpecification(Model):
        blob_duration: str
        display_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.MetricSpecification(Model):
        aggregation_type: str
        dimensions: list[Dimension]
        display_description: str
        display_name: str
        name: str
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[List[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                unit: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.Module(TrackedResource):
        activity_count: int
        content_link: ContentLink
        creation_time: datetime
        description: str
        error: ModuleErrorInfo
        etag: str
        id: str
        is_composite: bool
        is_global: bool
        last_modified_time: datetime
        location: str
        name: str
        provisioning_state: Union[str, ModuleProvisioningState]
        size_in_bytes: int
        tags: dict[str, str]
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                activity_count: Optional[int] = ..., 
                content_link: Optional[ContentLink] = ..., 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                error: Optional[ModuleErrorInfo] = ..., 
                etag: Optional[str] = ..., 
                is_composite: Optional[bool] = ..., 
                is_global: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                location: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ModuleProvisioningState]] = ..., 
                size_in_bytes: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.automation.models.ModuleCreateOrUpdateParameters(Model):
        content_link: ContentLink
        location: str
        name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_link: ContentLink, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ModuleErrorInfo(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ModuleListResult(Model):
        next_link: str
        value: list[Module]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Module]] = ..., 
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


    class azure.mgmt.automation.models.ModuleProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITIES_STORED = "ActivitiesStored"
        CANCELLED = "Cancelled"
        CONNECTION_TYPE_IMPORTED = "ConnectionTypeImported"
        CONTENT_DOWNLOADED = "ContentDownloaded"
        CONTENT_RETRIEVED = "ContentRetrieved"
        CONTENT_STORED = "ContentStored"
        CONTENT_VALIDATED = "ContentValidated"
        CREATED = "Created"
        CREATING = "Creating"
        FAILED = "Failed"
        MODULE_DATA_STORED = "ModuleDataStored"
        MODULE_IMPORT_RUNBOOK_COMPLETE = "ModuleImportRunbookComplete"
        RUNNING_IMPORT_MODULE_RUNBOOK = "RunningImportModuleRunbook"
        STARTING_IMPORT_MODULE_RUNBOOK = "StartingImportModuleRunbook"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.automation.models.ModuleUpdateParameters(Model):
        content_link: ContentLink
        location: str
        name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_link: Optional[ContentLink] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.NodeCount(Model):
        name: str
        properties: NodeCountProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[NodeCountProperties] = ..., 
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


    class azure.mgmt.automation.models.NodeCountProperties(Model):
        count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
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


    class azure.mgmt.automation.models.NodeCounts(Model):
        total_count: int
        value: list[NodeCount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                total_count: Optional[int] = ..., 
                value: Optional[List[NodeCount]] = ..., 
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


    class azure.mgmt.automation.models.NonAzureQueryProperties(Model):
        function_alias: str
        workspace_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                function_alias: Optional[str] = ..., 
                workspace_id: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.OperatingSystemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.automation.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str
        service_specification: OperationPropertiesFormatServiceSpecification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                service_specification: Optional[OperationPropertiesFormatServiceSpecification] = ..., 
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


    class azure.mgmt.automation.models.OperationDisplay(Model):
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


    class azure.mgmt.automation.models.OperationListResult(Model):
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Operation]] = ..., 
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


    class azure.mgmt.automation.models.OperationPropertiesFormatServiceSpecification(Model):
        log_specifications: list[LogSpecification]
        metric_specifications: list[MetricSpecification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_specifications: Optional[List[LogSpecification]] = ..., 
                metric_specifications: Optional[List[MetricSpecification]] = ..., 
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


    class azure.mgmt.automation.models.PrivateEndpointConnection(ProxyResource):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpointProperty
        private_link_service_connection_state: PrivateLinkServiceConnectionStateProperty
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_ids: Optional[List[str]] = ..., 
                private_endpoint: Optional[PrivateEndpointProperty] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty] = ..., 
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


    class azure.mgmt.automation.models.PrivateEndpointConnectionListResult(Model):
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
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


    class azure.mgmt.automation.models.PrivateEndpointProperty(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.PrivateLinkResource(ProxyResource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
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


    class azure.mgmt.automation.models.PrivateLinkResourceListResult(Model):
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateLinkResource]] = ..., 
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


    class azure.mgmt.automation.models.PrivateLinkServiceConnectionStateProperty(Model):
        actions_required: str
        description: str
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        RUNNING = "Running"


    class azure.mgmt.automation.models.ProxyResource(Resource):
        id: str
        name: str
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


    class azure.mgmt.automation.models.PythonPackageCreateParameters(Model):
        content_link: ContentLink
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_link: ContentLink, 
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


    class azure.mgmt.automation.models.PythonPackageUpdateParameters(Model):
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


    class azure.mgmt.automation.models.RawGraphicalRunbookContent(Model):
        runbook_definition: str
        runbook_type: Union[str, GraphRunbookType]
        schema_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                runbook_definition: Optional[str] = ..., 
                runbook_type: Optional[Union[str, GraphRunbookType]] = ..., 
                schema_version: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.Resource(Model):
        id: str
        name: str
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


    class azure.mgmt.automation.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.automation.models.RunAsCredentialAssociationProperty(Model):
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


    class azure.mgmt.automation.models.Runbook(TrackedResource):
        creation_time: datetime
        description: str
        draft: RunbookDraft
        etag: str
        id: str
        job_count: int
        last_modified_by: str
        last_modified_time: datetime
        location: str
        log_activity_trace: int
        log_progress: bool
        log_verbose: bool
        name: str
        output_types: list[str]
        parameters: dict[str, RunbookParameter]
        provisioning_state: str
        publish_content_link: ContentLink
        runbook_type: Union[str, RunbookTypeEnum]
        state: Union[str, RunbookState]
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                draft: Optional[RunbookDraft] = ..., 
                etag: Optional[str] = ..., 
                job_count: Optional[int] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                location: Optional[str] = ..., 
                log_activity_trace: Optional[int] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                output_types: Optional[List[str]] = ..., 
                parameters: Optional[Dict[str, RunbookParameter]] = ..., 
                provisioning_state: Optional[Literal[Succeeded]] = ..., 
                publish_content_link: Optional[ContentLink] = ..., 
                runbook_type: Optional[Union[str, RunbookTypeEnum]] = ..., 
                state: Optional[Union[str, RunbookState]] = ..., 
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


    class azure.mgmt.automation.models.RunbookAssociationProperty(Model):
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


    class azure.mgmt.automation.models.RunbookCreateOrUpdateDraftParameters(Model):
        runbook_content: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                runbook_content: str, 
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


    class azure.mgmt.automation.models.RunbookCreateOrUpdateDraftProperties(Model):
        description: str
        draft: RunbookDraft
        log_activity_trace: int
        log_progress: bool
        log_verbose: bool
        runbook_type: Union[str, RunbookTypeEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                draft: RunbookDraft, 
                log_activity_trace: Optional[int] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                runbook_type: Union[str, RunbookTypeEnum], 
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


    class azure.mgmt.automation.models.RunbookCreateOrUpdateParameters(Model):
        description: str
        draft: RunbookDraft
        location: str
        log_activity_trace: int
        log_progress: bool
        log_verbose: bool
        name: str
        publish_content_link: ContentLink
        runbook_type: Union[str, RunbookTypeEnum]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                draft: Optional[RunbookDraft] = ..., 
                location: Optional[str] = ..., 
                log_activity_trace: Optional[int] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                publish_content_link: Optional[ContentLink] = ..., 
                runbook_type: Union[str, RunbookTypeEnum], 
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


    class azure.mgmt.automation.models.RunbookDraft(Model):
        creation_time: datetime
        draft_content_link: ContentLink
        in_edit: bool
        last_modified_time: datetime
        output_types: list[str]
        parameters: dict[str, RunbookParameter]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                draft_content_link: Optional[ContentLink] = ..., 
                in_edit: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                output_types: Optional[List[str]] = ..., 
                parameters: Optional[Dict[str, RunbookParameter]] = ..., 
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


    class azure.mgmt.automation.models.RunbookDraftUndoEditResult(Model):
        request_id: str
        status_code: Union[str, HttpStatusCode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                request_id: Optional[str] = ..., 
                status_code: Optional[Union[str, HttpStatusCode]] = ..., 
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


    class azure.mgmt.automation.models.RunbookListResult(Model):
        next_link: str
        value: list[Runbook]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Runbook]] = ..., 
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


    class azure.mgmt.automation.models.RunbookParameter(Model):
        default_value: str
        is_mandatory: bool
        position: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                is_mandatory: Optional[bool] = ..., 
                position: Optional[int] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.RunbookState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDIT = "Edit"
        NEW = "New"
        PUBLISHED = "Published"


    class azure.mgmt.automation.models.RunbookTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAPH = "Graph"
        GRAPH_POWER_SHELL = "GraphPowerShell"
        GRAPH_POWER_SHELL_WORKFLOW = "GraphPowerShellWorkflow"
        POWER_SHELL = "PowerShell"
        POWER_SHELL_WORKFLOW = "PowerShellWorkflow"
        PYTHON2 = "Python2"
        PYTHON3 = "Python3"
        SCRIPT = "Script"


    class azure.mgmt.automation.models.RunbookUpdateParameters(Model):
        description: str
        location: str
        log_activity_trace: int
        log_progress: bool
        log_verbose: bool
        name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                location: Optional[str] = ..., 
                log_activity_trace: Optional[int] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.SUCScheduleProperties(Model):
        advanced_schedule: AdvancedSchedule
        creation_time: datetime
        description: str
        expiry_time: datetime
        expiry_time_offset_minutes: float
        frequency: Union[str, ScheduleFrequency]
        interval: int
        is_enabled: bool
        last_modified_time: datetime
        next_run: datetime
        next_run_offset_minutes: float
        start_time: datetime
        start_time_offset_minutes: float
        time_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_schedule: Optional[AdvancedSchedule] = ..., 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                expiry_time_offset_minutes: Optional[float] = ..., 
                frequency: Optional[Union[str, ScheduleFrequency]] = ..., 
                interval: Optional[int] = ..., 
                is_enabled: bool = False, 
                last_modified_time: Optional[datetime] = ..., 
                next_run: Optional[datetime] = ..., 
                next_run_offset_minutes: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.Schedule(ProxyResource):
        advanced_schedule: AdvancedSchedule
        creation_time: datetime
        description: str
        expiry_time: datetime
        expiry_time_offset_minutes: float
        frequency: Union[str, ScheduleFrequency]
        id: str
        interval: any
        is_enabled: bool
        last_modified_time: datetime
        name: str
        next_run: datetime
        next_run_offset_minutes: float
        start_time: datetime
        start_time_offset_minutes: float
        time_zone: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_schedule: Optional[AdvancedSchedule] = ..., 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                expiry_time_offset_minutes: Optional[float] = ..., 
                frequency: Optional[Union[str, ScheduleFrequency]] = ..., 
                interval: Optional[Any] = ..., 
                is_enabled: bool = False, 
                last_modified_time: Optional[datetime] = ..., 
                next_run: Optional[datetime] = ..., 
                next_run_offset_minutes: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ScheduleAssociationProperty(Model):
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


    class azure.mgmt.automation.models.ScheduleCreateOrUpdateParameters(Model):
        advanced_schedule: AdvancedSchedule
        description: str
        expiry_time: datetime
        frequency: Union[str, ScheduleFrequency]
        interval: any
        name: str
        start_time: datetime
        time_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                advanced_schedule: Optional[AdvancedSchedule] = ..., 
                description: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                frequency: Union[str, ScheduleFrequency], 
                interval: Optional[Any] = ..., 
                name: str, 
                start_time: datetime, 
                time_zone: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.ScheduleDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.automation.models.ScheduleFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        HOUR = "Hour"
        MINUTE = "Minute"
        MONTH = "Month"
        ONE_TIME = "OneTime"
        WEEK = "Week"


    class azure.mgmt.automation.models.ScheduleListResult(Model):
        next_link: str
        value: list[Schedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Schedule]] = ..., 
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


    class azure.mgmt.automation.models.ScheduleUpdateParameters(Model):
        description: str
        is_enabled: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.Sku(Model):
        capacity: int
        family: str
        name: Union[str, SkuNameEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Union[str, SkuNameEnum], 
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


    class azure.mgmt.automation.models.SkuNameEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"


    class azure.mgmt.automation.models.SoftwareUpdateConfiguration(Model):
        created_by: str
        creation_time: datetime
        error: ErrorResponse
        id: str
        last_modified_by: str
        last_modified_time: datetime
        name: str
        provisioning_state: str
        schedule_info: SUCScheduleProperties
        tasks: SoftwareUpdateConfigurationTasks
        type: str
        update_configuration: UpdateConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
                schedule_info: SUCScheduleProperties, 
                tasks: Optional[SoftwareUpdateConfigurationTasks] = ..., 
                update_configuration: UpdateConfiguration, 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationCollectionItem(Model):
        creation_time: datetime
        frequency: Union[str, ScheduleFrequency]
        id: str
        last_modified_time: datetime
        name: str
        next_run: datetime
        provisioning_state: str
        start_time: datetime
        tasks: SoftwareUpdateConfigurationTasks
        update_configuration: UpdateConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduleFrequency]] = ..., 
                next_run: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                tasks: Optional[SoftwareUpdateConfigurationTasks] = ..., 
                update_configuration: Optional[UpdateConfiguration] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationListResult(Model):
        value: list[SoftwareUpdateConfigurationCollectionItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SoftwareUpdateConfigurationCollectionItem]] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationMachineRun(Model):
        configured_duration: str
        correlation_id: str
        created_by: str
        creation_time: datetime
        end_time: datetime
        error: ErrorResponse
        id: str
        job: JobNavigation
        last_modified_by: str
        last_modified_time: datetime
        name: str
        os_type: str
        software_update_configuration: UpdateConfigurationNavigation
        source_computer_id: str
        start_time: datetime
        status: str
        target_computer: str
        target_computer_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
                job: Optional[JobNavigation] = ..., 
                software_update_configuration: Optional[UpdateConfigurationNavigation] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationMachineRunListResult(Model):
        next_link: str
        value: list[SoftwareUpdateConfigurationMachineRun]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SoftwareUpdateConfigurationMachineRun]] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRun(Model):
        computer_count: int
        configured_duration: str
        created_by: str
        creation_time: datetime
        end_time: datetime
        failed_count: int
        id: str
        last_modified_by: str
        last_modified_time: datetime
        name: str
        os_type: str
        software_update_configuration: UpdateConfigurationNavigation
        start_time: datetime
        status: str
        tasks: SoftwareUpdateConfigurationRunTasks

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                software_update_configuration: Optional[UpdateConfigurationNavigation] = ..., 
                tasks: Optional[SoftwareUpdateConfigurationRunTasks] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRunListResult(Model):
        next_link: str
        value: list[SoftwareUpdateConfigurationRun]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SoftwareUpdateConfigurationRun]] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRunTaskProperties(Model):
        job_id: str
        source: str
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ..., 
                source: Optional[str] = ..., 
                status: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRunTasks(Model):
        post_task: SoftwareUpdateConfigurationRunTaskProperties
        pre_task: SoftwareUpdateConfigurationRunTaskProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                post_task: Optional[SoftwareUpdateConfigurationRunTaskProperties] = ..., 
                pre_task: Optional[SoftwareUpdateConfigurationRunTaskProperties] = ..., 
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


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationTasks(Model):
        post_task: TaskProperties
        pre_task: TaskProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                post_task: Optional[TaskProperties] = ..., 
                pre_task: Optional[TaskProperties] = ..., 
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


    class azure.mgmt.automation.models.SourceControl(ProxyResource):
        auto_sync: bool
        branch: str
        creation_time: datetime
        description: str
        folder_path: str
        id: str
        last_modified_time: datetime
        name: str
        publish_runbook: bool
        repo_url: str
        source_type: Union[str, SourceType]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_sync: Optional[bool] = ..., 
                branch: Optional[str] = ..., 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                folder_path: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                publish_runbook: Optional[bool] = ..., 
                repo_url: Optional[str] = ..., 
                source_type: Optional[Union[str, SourceType]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlCreateOrUpdateParameters(Model):
        auto_sync: bool
        branch: str
        description: str
        folder_path: str
        publish_runbook: bool
        repo_url: str
        security_token: SourceControlSecurityTokenProperties
        source_type: Union[str, SourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_sync: Optional[bool] = ..., 
                branch: Optional[str] = ..., 
                description: Optional[str] = ..., 
                folder_path: Optional[str] = ..., 
                publish_runbook: Optional[bool] = ..., 
                repo_url: Optional[str] = ..., 
                security_token: Optional[SourceControlSecurityTokenProperties] = ..., 
                source_type: Optional[Union[str, SourceType]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlListResult(Model):
        next_link: str
        value: list[SourceControl]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SourceControl]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlSecurityTokenProperties(Model):
        access_token: str
        refresh_token: str
        token_type: Union[str, TokenType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                refresh_token: Optional[str] = ..., 
                token_type: Optional[Union[str, TokenType]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlSyncJob(Model):
        creation_time: datetime
        end_time: datetime
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        source_control_sync_job_id: str
        start_time: datetime
        sync_type: Union[str, SyncType]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                source_control_sync_job_id: Optional[str] = ..., 
                sync_type: Optional[Union[str, SyncType]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlSyncJobById(Model):
        creation_time: datetime
        end_time: datetime
        exception: str
        id: str
        provisioning_state: Union[str, ProvisioningState]
        source_control_sync_job_id: str
        start_time: datetime
        sync_type: Union[str, SyncType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                exception: Optional[str] = ..., 
                id: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                source_control_sync_job_id: Optional[str] = ..., 
                sync_type: Optional[Union[str, SyncType]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlSyncJobCreateParameters(Model):
        commit_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                commit_id: str, 
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


    class azure.mgmt.automation.models.SourceControlSyncJobListResult(Model):
        next_link: str
        value: list[SourceControlSyncJob]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SourceControlSyncJob]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlSyncJobStream(Model):
        id: str
        source_control_sync_job_stream_id: str
        stream_type: Union[str, StreamType]
        summary: str
        time: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_control_sync_job_stream_id: Optional[str] = ..., 
                stream_type: Optional[Union[str, StreamType]] = ..., 
                summary: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.SourceControlSyncJobStreamById(Model):
        id: str
        source_control_sync_job_stream_id: str
        stream_text: str
        stream_type: Union[str, StreamType]
        summary: str
        time: datetime
        value: dict[str, JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_control_sync_job_stream_id: Optional[str] = ..., 
                stream_text: Optional[str] = ..., 
                stream_type: Optional[Union[str, StreamType]] = ..., 
                summary: Optional[str] = ..., 
                value: Optional[Dict[str, JSON]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlSyncJobStreamsListBySyncJob(Model):
        next_link: str
        value: list[SourceControlSyncJobStream]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SourceControlSyncJobStream]] = ..., 
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


    class azure.mgmt.automation.models.SourceControlUpdateParameters(Model):
        auto_sync: bool
        branch: str
        description: str
        folder_path: str
        publish_runbook: bool
        security_token: SourceControlSecurityTokenProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_sync: Optional[bool] = ..., 
                branch: Optional[str] = ..., 
                description: Optional[str] = ..., 
                folder_path: Optional[str] = ..., 
                publish_runbook: Optional[bool] = ..., 
                security_token: Optional[SourceControlSecurityTokenProperties] = ..., 
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


    class azure.mgmt.automation.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GIT_HUB = "GitHub"
        VSO_GIT = "VsoGit"
        VSO_TFVC = "VsoTfvc"


    class azure.mgmt.automation.models.Statistics(Model):
        counter_property: str
        counter_value: int
        end_time: datetime
        id: str
        start_time: datetime

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


    class azure.mgmt.automation.models.StatisticsListResult(Model):
        value: list[Statistics]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Statistics]] = ..., 
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


    class azure.mgmt.automation.models.StreamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        OUTPUT = "Output"


    class azure.mgmt.automation.models.SyncType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_SYNC = "FullSync"
        PARTIAL_SYNC = "PartialSync"


    class azure.mgmt.automation.models.SystemData(Model):
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


    class azure.mgmt.automation.models.TagOperators(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ANY = "Any"


    class azure.mgmt.automation.models.TagSettingsProperties(Model):
        filter_operator: Union[str, TagOperators]
        tags: dict[str, list[str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filter_operator: Optional[Union[str, TagOperators]] = ..., 
                tags: Optional[Dict[str, List[str]]] = ..., 
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


    class azure.mgmt.automation.models.TargetProperties(Model):
        azure_queries: list[AzureQueryProperties]
        non_azure_queries: list[NonAzureQueryProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_queries: Optional[List[AzureQueryProperties]] = ..., 
                non_azure_queries: Optional[List[NonAzureQueryProperties]] = ..., 
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


    class azure.mgmt.automation.models.TaskProperties(Model):
        parameters: dict[str, str]
        source: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[Dict[str, str]] = ..., 
                source: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.TestJob(Model):
        creation_time: datetime
        end_time: datetime
        exception: str
        last_modified_time: datetime
        last_status_modified_time: datetime
        log_activity_trace: int
        parameters: dict[str, str]
        run_on: str
        start_time: datetime
        status: str
        status_details: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                end_time: Optional[datetime] = ..., 
                exception: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                last_status_modified_time: Optional[datetime] = ..., 
                log_activity_trace: Optional[int] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                status_details: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.TestJobCreateParameters(Model):
        parameters: dict[str, str]
        run_on: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.TokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OAUTH = "Oauth"
        PERSONAL_ACCESS_TOKEN = "PersonalAccessToken"


    class azure.mgmt.automation.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
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


    class azure.mgmt.automation.models.TypeField(Model):
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


    class azure.mgmt.automation.models.TypeFieldListResult(Model):
        value: list[TypeField]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[TypeField]] = ..., 
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


    class azure.mgmt.automation.models.UpdateConfiguration(Model):
        azure_virtual_machines: list[str]
        duration: timedelta
        linux: LinuxProperties
        non_azure_computer_names: list[str]
        operating_system: Union[str, OperatingSystemType]
        targets: TargetProperties
        windows: WindowsProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_virtual_machines: Optional[List[str]] = ..., 
                duration: Optional[timedelta] = ..., 
                linux: Optional[LinuxProperties] = ..., 
                non_azure_computer_names: Optional[List[str]] = ..., 
                operating_system: Union[str, OperatingSystemType], 
                targets: Optional[TargetProperties] = ..., 
                windows: Optional[WindowsProperties] = ..., 
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


    class azure.mgmt.automation.models.UpdateConfigurationNavigation(Model):
        name: str

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


    class azure.mgmt.automation.models.Usage(Model):
        current_value: float
        id: str
        limit: int
        name: UsageCounterName
        throttle_status: str
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_value: Optional[float] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[UsageCounterName] = ..., 
                throttle_status: Optional[str] = ..., 
                unit: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.UsageCounterName(Model):
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


    class azure.mgmt.automation.models.UsageListResult(Model):
        value: list[Usage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Usage]] = ..., 
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


    class azure.mgmt.automation.models.UserAssignedIdentitiesProperties(Model):
        client_id: str
        principal_id: str

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


    class azure.mgmt.automation.models.Variable(ProxyResource):
        creation_time: datetime
        description: str
        id: str
        is_encrypted: bool
        last_modified_time: datetime
        name: str
        type: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                is_encrypted: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.VariableCreateOrUpdateParameters(Model):
        description: str
        is_encrypted: bool
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_encrypted: Optional[bool] = ..., 
                name: str, 
                value: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.VariableListResult(Model):
        next_link: str
        value: list[Variable]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Variable]] = ..., 
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


    class azure.mgmt.automation.models.VariableUpdateParameters(Model):
        description: str
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.Watcher(Resource):
        creation_time: datetime
        description: str
        etag: str
        execution_frequency_in_seconds: int
        id: str
        last_modified_by: str
        last_modified_time: datetime
        location: str
        name: str
        script_name: str
        script_parameters: dict[str, str]
        script_run_on: str
        status: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                execution_frequency_in_seconds: Optional[int] = ..., 
                location: Optional[str] = ..., 
                script_name: Optional[str] = ..., 
                script_parameters: Optional[Dict[str, str]] = ..., 
                script_run_on: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.WatcherListResult(Model):
        next_link: str
        value: list[Watcher]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Watcher]] = ..., 
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


    class azure.mgmt.automation.models.WatcherUpdateParameters(Model):
        execution_frequency_in_seconds: int
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                execution_frequency_in_seconds: Optional[int] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.Webhook(ProxyResource):
        creation_time: datetime
        description: str
        expiry_time: datetime
        id: str
        is_enabled: bool
        last_invoked_time: datetime
        last_modified_by: str
        last_modified_time: datetime
        name: str
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty
        type: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_enabled: bool = False, 
                last_invoked_time: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.WebhookCreateOrUpdateParameters(Model):
        expiry_time: datetime
        is_enabled: bool
        name: str
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                is_enabled: Optional[bool] = ..., 
                name: str, 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.WebhookListResult(Model):
        next_link: str
        value: list[Webhook]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Webhook]] = ..., 
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


    class azure.mgmt.automation.models.WebhookUpdateParameters(Model):
        description: str
        is_enabled: bool
        name: str
        parameters: dict[str, str]
        run_on: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.WindowsProperties(Model):
        excluded_kb_numbers: list[str]
        included_kb_numbers: list[str]
        included_update_classifications: Union[str, WindowsUpdateClasses]
        reboot_setting: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                excluded_kb_numbers: Optional[List[str]] = ..., 
                included_kb_numbers: Optional[List[str]] = ..., 
                included_update_classifications: Optional[Union[str, WindowsUpdateClasses]] = ..., 
                reboot_setting: Optional[str] = ..., 
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


    class azure.mgmt.automation.models.WindowsUpdateClasses(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        DEFINITION = "Definition"
        FEATURE_PACK = "FeaturePack"
        SECURITY = "Security"
        SERVICE_PACK = "ServicePack"
        TOOLS = "Tools"
        UNCLASSIFIED = "Unclassified"
        UPDATES = "Updates"
        UPDATE_ROLLUP = "UpdateRollup"


    class azure.mgmt.automation.models.WorkerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HYBRID_V1 = "HybridV1"
        HYBRID_V2 = "HybridV2"


namespace azure.mgmt.automation.operations

    class azure.mgmt.automation.operations.ActivityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                activity_name: str, 
                **kwargs: Any
            ) -> Activity: ...

        @distributed_trace
        def list_by_module(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                **kwargs: Any
            ) -> Iterable[Activity]: ...


    class azure.mgmt.automation.operations.AgentRegistrationInformationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AgentRegistration: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: AgentRegistrationRegenerateKeyParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentRegistration: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentRegistration: ...


    class azure.mgmt.automation.operations.AutomationAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: AutomationAccountCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[AutomationAccount]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[AutomationAccount]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: AutomationAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AutomationAccount: ...


    class azure.mgmt.automation.operations.AutomationClientOperationsMixin(AutomationClientMixinABC):

        @overload
        def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: GraphicalRunbookContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...

        @overload
        def convert_graph_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GraphicalRunbookContent: ...


    class azure.mgmt.automation.operations.CertificateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: CertificateCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> Certificate: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Certificate]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: CertificateUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                certificate_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Certificate: ...


    class azure.mgmt.automation.operations.ConnectionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: ConnectionCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Connection]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: ConnectionUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Connection: ...


    class azure.mgmt.automation.operations.ConnectionTypeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                parameters: ConnectionTypeCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionType: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionType: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                connection_type_name: str, 
                **kwargs: Any
            ) -> ConnectionType: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[ConnectionType]: ...


    class azure.mgmt.automation.operations.CredentialOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: CredentialCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                **kwargs: Any
            ) -> Credential: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Credential]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: CredentialUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                credential_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Credential: ...


    class azure.mgmt.automation.operations.DeletedAutomationAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> DeletedAutomationAccountListResult: ...


    class azure.mgmt.automation.operations.DscCompilationJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                compilation_job_name: str, 
                parameters: DscCompilationJobCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DscCompilationJob]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                compilation_job_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DscCompilationJob]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                compilation_job_name: str, 
                **kwargs: Any
            ) -> DscCompilationJob: ...

        @distributed_trace
        def get_stream(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_id: str, 
                job_stream_id: str, 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[DscCompilationJob]: ...


    class azure.mgmt.automation.operations.DscCompilationJobStreamOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_id: str, 
                **kwargs: Any
            ) -> JobStreamListResult: ...


    class azure.mgmt.automation.operations.DscConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: DscConfigurationCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: str, 
                *, 
                content_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @distributed_trace
        def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                inlinecount: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[DscConfiguration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: Optional[DscConfigurationUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscConfiguration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                configuration_name: str, 
                parameters: Optional[str] = None, 
                *, 
                content_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> DscConfiguration: ...


    class azure.mgmt.automation.operations.DscNodeConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                parameters: DscNodeConfigurationCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DscNodeConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DscNodeConfiguration]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_configuration_name: str, 
                **kwargs: Any
            ) -> DscNodeConfiguration: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                inlinecount: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[DscNodeConfiguration]: ...


    class azure.mgmt.automation.operations.DscNodeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                **kwargs: Any
            ) -> DscNode: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                inlinecount: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[DscNode]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                dsc_node_update_parameters: DscNodeUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscNode: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                dsc_node_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscNode: ...


    class azure.mgmt.automation.operations.FieldsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> Iterable[TypeField]: ...


    class azure.mgmt.automation.operations.HybridRunbookWorkerGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_creation_parameters: HybridRunbookWorkerGroupCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_creation_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[HybridRunbookWorkerGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_updation_parameters: HybridRunbookWorkerGroupCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_group_updation_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorkerGroup: ...


    class azure.mgmt.automation.operations.HybridRunbookWorkersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: HybridRunbookWorkerCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @distributed_trace
        def list_by_hybrid_runbook_worker_group(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[HybridRunbookWorker]: ...

        @overload
        def move(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_move_parameters: HybridRunbookWorkerMoveParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def move(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_move_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.automation.operations.JobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                parameters: JobCreateParameters, 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                parameters: IO[bytes], 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def get_output(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def get_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[JobCollectionItem]: ...

        @distributed_trace
        def resume(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def suspend(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.automation.operations.JobScheduleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                parameters: JobScheduleCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobSchedule: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JobSchedule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_schedule_id: str, 
                **kwargs: Any
            ) -> JobSchedule: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[JobSchedule]: ...


    class azure.mgmt.automation.operations.JobStreamOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                job_stream_id: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                filter: Optional[str] = None, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[JobStream]: ...


    class azure.mgmt.automation.operations.KeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> KeyListResult: ...


    class azure.mgmt.automation.operations.LinkedWorkspaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> LinkedWorkspace: ...


    class azure.mgmt.automation.operations.ModuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: ModuleCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Module]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: ModuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...


    class azure.mgmt.automation.operations.NodeCountInformationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                count_type: Union[str, CountType], 
                **kwargs: Any
            ) -> NodeCounts: ...


    class azure.mgmt.automation.operations.NodeReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                report_id: str, 
                **kwargs: Any
            ) -> DscNodeReport: ...

        @distributed_trace
        def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                report_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list_by_node(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[DscNodeReport]: ...


    class azure.mgmt.automation.operations.ObjectDataTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_fields_by_module_and_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> Iterable[TypeField]: ...

        @distributed_trace
        def list_fields_by_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> Iterable[TypeField]: ...


    class azure.mgmt.automation.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.automation.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnection]: ...


    class azure.mgmt.automation.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def automation(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


    class azure.mgmt.automation.operations.Python2PackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Module]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...


    class azure.mgmt.automation.operations.Python3PackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> Module: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Module]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: PythonPackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Module: ...


    class azure.mgmt.automation.operations.RunbookDraftOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_replace_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                runbook_content: IO[bytes], 
                **kwargs: Any
            ) -> LROPoller[Iterator[bytes]]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> RunbookDraft: ...

        @distributed_trace
        def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def undo_edit(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> RunbookDraftUndoEditResult: ...


    class azure.mgmt.automation.operations.RunbookOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_publish(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: RunbookCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> Runbook: ...

        @distributed_trace
        def get_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Runbook]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: RunbookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Runbook: ...


    class azure.mgmt.automation.operations.ScheduleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: ScheduleCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[Schedule]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[Schedule]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: ScheduleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                schedule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...


    class azure.mgmt.automation.operations.SoftwareUpdateConfigurationMachineRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_id(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_machine_run_id: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationMachineRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                client_request_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationMachineRunListResult: ...


    class azure.mgmt.automation.operations.SoftwareUpdateConfigurationRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_id(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_run_id: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                client_request_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationRunListResult: ...


    class azure.mgmt.automation.operations.SoftwareUpdateConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                parameters: SoftwareUpdateConfiguration, 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                parameters: IO[bytes], 
                client_request_id: Optional[str] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_name(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                client_request_id: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                client_request_id: Optional[str] = None, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationListResult: ...


    class azure.mgmt.automation.operations.SourceControlOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: SourceControlCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                **kwargs: Any
            ) -> SourceControl: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[SourceControl]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: SourceControlUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControl: ...


    class azure.mgmt.automation.operations.SourceControlSyncJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                parameters: SourceControlSyncJobCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControlSyncJob: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SourceControlSyncJob: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                **kwargs: Any
            ) -> SourceControlSyncJobById: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[SourceControlSyncJob]: ...


    class azure.mgmt.automation.operations.SourceControlSyncJobStreamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                stream_id: str, 
                **kwargs: Any
            ) -> SourceControlSyncJobStreamById: ...

        @distributed_trace
        def list_by_sync_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                source_control_name: str, 
                source_control_sync_job_id: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[SourceControlSyncJobStream]: ...


    class azure.mgmt.automation.operations.StatisticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Statistics]: ...


    class azure.mgmt.automation.operations.TestJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: TestJobCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestJob: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TestJob: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> TestJob: ...

        @distributed_trace
        def resume(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def suspend(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.automation.operations.TestJobStreamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                job_stream_id: str, 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_test_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[JobStream]: ...


    class azure.mgmt.automation.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


    class azure.mgmt.automation.operations.VariableOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: VariableCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                **kwargs: Any
            ) -> Variable: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> Iterable[Variable]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: VariableUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                variable_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Variable: ...


    class azure.mgmt.automation.operations.WatcherOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: Watcher, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Watcher: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Watcher]: ...

        @distributed_trace
        def start(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: WatcherUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                watcher_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Watcher: ...


    class azure.mgmt.automation.operations.WebhookOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: WebhookCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def generate_uri(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                **kwargs: Any
            ) -> Webhook: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[Webhook]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: WebhookUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                webhook_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Webhook: ...


```