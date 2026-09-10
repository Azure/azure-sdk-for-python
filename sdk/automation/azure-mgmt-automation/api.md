```py
namespace azure.mgmt.automation

    class azure.mgmt.automation.AutomationClient(_AutomationClientOperationsMixin): implements ContextManager 
        activity: ActivityOperations
        agent_registration_information: AgentRegistrationInformationOperations
        automation_account: AutomationAccountOperations
        certificate: CertificateOperations
        connection: ConnectionOperations
        connection_type: ConnectionTypeOperations
        credential: CredentialOperations
        deleted_automation_accounts: DeletedAutomationAccountsOperations
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
        package: PackageOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        python2_package: Python2PackageOperations
        python3_package: Python3PackageOperations
        runbook: RunbookOperations
        runbook_draft: RunbookDraftOperations
        runtime_environments: RuntimeEnvironmentsOperations
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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.automation.aio

    class azure.mgmt.automation.aio.AutomationClient(_AutomationClientOperationsMixin): implements AsyncContextManager 
        activity: ActivityOperations
        agent_registration_information: AgentRegistrationInformationOperations
        automation_account: AutomationAccountOperations
        certificate: CertificateOperations
        connection: ConnectionOperations
        connection_type: ConnectionTypeOperations
        credential: CredentialOperations
        deleted_automation_accounts: DeletedAutomationAccountsOperations
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
        package: PackageOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        python2_package: Python2PackageOperations
        python3_package: Python3PackageOperations
        runbook: RunbookOperations
        runbook_draft: RunbookDraftOperations
        runtime_environments: RuntimeEnvironmentsOperations
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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


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
            ) -> AsyncItemPaged[Activity]: ...


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
        def list(self, **kwargs: Any) -> AsyncItemPaged[AutomationAccount]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AutomationAccount]: ...

        @distributed_trace
        def list_deleted_runbooks(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeletedRunbook]: ...

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
            ) -> AsyncItemPaged[Certificate]: ...

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
            ) -> AsyncItemPaged[Connection]: ...

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
            ) -> AsyncItemPaged[ConnectionType]: ...


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
            ) -> AsyncItemPaged[Credential]: ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
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
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                inlinecount: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DscConfiguration]: ...

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
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
                *, 
                filter: Optional[str] = ..., 
                inlinecount: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DscNodeConfiguration]: ...


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
                *, 
                filter: Optional[str] = ..., 
                inlinecount: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DscNode]: ...

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
            ) -> AsyncItemPaged[TypeField]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[HybridRunbookWorkerGroup]: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[HybridRunbookWorker]: ...

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

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: Optional[HybridRunbookWorkerCreateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: Optional[HybridRunbookWorkerCreateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...


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
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                parameters: JobCreateParameters, 
                *, 
                client_request_id: Optional[str] = ..., 
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
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace_async
        async def get_output(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace_async
        async def get_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobCollectionItem]: ...

        @distributed_trace_async
        async def resume(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def suspend(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobSchedule]: ...


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
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobStream]: ...


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
            ) -> AsyncItemPaged[Module]: ...

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
            ) -> str: ...

        @distributed_trace
        def list_by_node(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DscNodeReport]: ...


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
            ) -> AsyncItemPaged[TypeField]: ...

        @distributed_trace
        def list_fields_by_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TypeField]: ...


    class azure.mgmt.automation.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.automation.aio.operations.PackageOperations:

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
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> Package: ...

        @distributed_trace
        def list_by_runtime_environment(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Package]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...


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
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


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
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


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
            ) -> AsyncItemPaged[Module]: ...

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
            ) -> AsyncItemPaged[Module]: ...

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
                runbook_content: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

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
            ) -> str: ...

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
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Runbook]: ...

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


    class azure.mgmt.automation.aio.operations.RuntimeEnvironmentsOperations:

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
                runtime_environment_name: str, 
                parameters: RuntimeEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: RuntimeEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RuntimeEnvironment]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: RuntimeEnvironmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: RuntimeEnvironmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...


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
            ) -> AsyncItemPaged[Schedule]: ...

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
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationMachineRun: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[str] = ..., 
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
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationRun: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[str] = ..., 
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
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                parameters: SoftwareUpdateConfiguration, 
                *, 
                client_request_id: Optional[str] = ..., 
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
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_name(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SourceControl]: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SourceControlSyncJob]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SourceControlSyncJobStream]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Statistics]: ...


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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[JobStream]: ...


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
            ) -> AsyncItemPaged[Usage]: ...


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
            ) -> AsyncItemPaged[Variable]: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Watcher]: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Webhook]: ...

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

    class azure.mgmt.automation.models.Activity(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ActivityProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[ActivityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ActivityOutputType(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ActivityParameter(_Model):
        description: Optional[str]
        is_dynamic: Optional[bool]
        is_mandatory: Optional[bool]
        name: Optional[str]
        position: Optional[int]
        type: Optional[str]
        validation_set: Optional[list[ActivityParameterValidationSet]]
        value_from_pipeline: Optional[bool]
        value_from_pipeline_by_property_name: Optional[bool]
        value_from_remaining_arguments: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_dynamic: Optional[bool] = ..., 
                is_mandatory: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                position: Optional[int] = ..., 
                type: Optional[str] = ..., 
                validation_set: Optional[list[ActivityParameterValidationSet]] = ..., 
                value_from_pipeline: Optional[bool] = ..., 
                value_from_pipeline_by_property_name: Optional[bool] = ..., 
                value_from_remaining_arguments: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ActivityParameterSet(_Model):
        name: Optional[str]
        parameters: Optional[list[ActivityParameter]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[list[ActivityParameter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ActivityParameterValidationSet(_Model):
        member_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                member_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ActivityProperties(_Model):
        creation_time: Optional[datetime]
        definition: Optional[str]
        description: Optional[str]
        last_modified_time: Optional[datetime]
        output_types: Optional[list[ActivityOutputType]]
        parameter_sets: Optional[list[ActivityParameterSet]]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                definition: Optional[str] = ..., 
                description: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                output_types: Optional[list[ActivityOutputType]] = ..., 
                parameter_sets: Optional[list[ActivityParameterSet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AdvancedSchedule(_Model):
        month_days: Optional[list[int]]
        monthly_occurrences: Optional[list[AdvancedScheduleMonthlyOccurrence]]
        week_days: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                month_days: Optional[list[int]] = ..., 
                monthly_occurrences: Optional[list[AdvancedScheduleMonthlyOccurrence]] = ..., 
                week_days: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AdvancedScheduleMonthlyOccurrence(_Model):
        day: Optional[Union[str, ScheduleDay]]
        occurrence: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                day: Optional[Union[str, ScheduleDay]] = ..., 
                occurrence: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AgentRegistration(_Model):
        dsc_meta_configuration: Optional[str]
        endpoint: Optional[str]
        id: Optional[str]
        keys_property: Optional[AgentRegistrationKeys]

        @overload
        def __init__(
                self, 
                *, 
                dsc_meta_configuration: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                id: Optional[str] = ..., 
                keys_property: Optional[AgentRegistrationKeys] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AgentRegistrationKeyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "primary"
        SECONDARY = "secondary"


    class azure.mgmt.automation.models.AgentRegistrationKeys(_Model):
        primary: Optional[str]
        secondary: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary: Optional[str] = ..., 
                secondary: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AgentRegistrationRegenerateKeyParameter(_Model):
        key_name: Union[str, AgentRegistrationKeyName]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Union[str, AgentRegistrationKeyName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AutomationAccount(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[AutomationAccountProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[Identity] = ..., 
                location: str, 
                properties: Optional[AutomationAccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.AutomationAccountCreateOrUpdateParameters(_Model):
        identity: Optional[Identity]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[AutomationAccountCreateOrUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[AutomationAccountCreateOrUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.AutomationAccountCreateOrUpdateProperties(_Model):
        disable_local_auth: Optional[bool]
        encryption: Optional[EncryptionProperties]
        public_network_access: Optional[bool]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                public_network_access: Optional[bool] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AutomationAccountProperties(_Model):
        automation_hybrid_service_url: Optional[str]
        creation_time: Optional[datetime]
        description: Optional[str]
        disable_local_auth: Optional[bool]
        encryption: Optional[EncryptionProperties]
        last_modified_by: Optional[str]
        last_modified_time: Optional[datetime]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        public_network_access: Optional[bool]
        sku: Optional[Sku]
        state: Optional[Union[str, AutomationAccountState]]

        @overload
        def __init__(
                self, 
                *, 
                automation_hybrid_service_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                last_modified_by: Optional[str] = ..., 
                private_endpoint_connections: Optional[list[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[bool] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AutomationAccountState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OK = "Ok"
        SUSPENDED = "Suspended"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.automation.models.AutomationAccountUpdateParameters(_Model):
        identity: Optional[Identity]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[AutomationAccountUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[AutomationAccountUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.AutomationAccountUpdateProperties(_Model):
        disable_local_auth: Optional[bool]
        encryption: Optional[EncryptionProperties]
        public_network_access: Optional[bool]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[EncryptionProperties] = ..., 
                public_network_access: Optional[bool] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AutomationErrorResponse(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.AutomationKeyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.automation.models.AutomationKeyPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        READ = "Read"


    class azure.mgmt.automation.models.AzureQueryProperties(_Model):
        locations: Optional[list[str]]
        scope: Optional[list[str]]
        tag_settings: Optional[TagSettingsProperties]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                scope: Optional[list[str]] = ..., 
                tag_settings: Optional[TagSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Certificate(ProxyResource):
        id: str
        name: str
        properties: Optional[CertificateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CertificateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.CertificateCreateOrUpdateParameters(_Model):
        name: str
        properties: CertificateCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: CertificateCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.CertificateCreateOrUpdateProperties(_Model):
        base64_value: str
        description: Optional[str]
        is_exportable: Optional[bool]
        thumbprint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base64_value: str, 
                description: Optional[str] = ..., 
                is_exportable: Optional[bool] = ..., 
                thumbprint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.CertificateProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        expiry_time: Optional[datetime]
        is_exportable: Optional[bool]
        last_modified_time: Optional[datetime]
        thumbprint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.CertificateUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[CertificateUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[CertificateUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.CertificateUpdateProperties(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Connection(ProxyResource):
        id: str
        name: str
        properties: Optional[ConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ConnectionCreateOrUpdateParameters(_Model):
        name: str
        properties: ConnectionCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: ConnectionCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ConnectionCreateOrUpdateProperties(_Model):
        connection_type: ConnectionTypeAssociationProperty
        description: Optional[str]
        field_definition_values: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                connection_type: ConnectionTypeAssociationProperty, 
                description: Optional[str] = ..., 
                field_definition_values: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ConnectionProperties(_Model):
        connection_type: Optional[ConnectionTypeAssociationProperty]
        creation_time: Optional[datetime]
        description: Optional[str]
        field_definition_values: Optional[dict[str, str]]
        last_modified_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                connection_type: Optional[ConnectionTypeAssociationProperty] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ConnectionType(ProxyResource):
        id: str
        name: str
        properties: Optional[ConnectionTypeProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectionTypeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ConnectionTypeAssociationProperty(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ConnectionTypeCreateOrUpdateParameters(_Model):
        name: str
        properties: ConnectionTypeCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: ConnectionTypeCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ConnectionTypeCreateOrUpdateProperties(_Model):
        field_definitions: dict[str, FieldDefinition]
        is_global: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                field_definitions: dict[str, FieldDefinition], 
                is_global: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ConnectionTypeProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        field_definitions: Optional[dict[str, FieldDefinition]]
        is_global: Optional[bool]
        last_modified_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_global: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ConnectionUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[ConnectionUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[ConnectionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ConnectionUpdateProperties(_Model):
        description: Optional[str]
        field_definition_values: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                field_definition_values: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ContentHash(_Model):
        algorithm: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                algorithm: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ContentLink(_Model):
        content_hash: Optional[ContentHash]
        uri: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_hash: Optional[ContentHash] = ..., 
                uri: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ContentSource(_Model):
        hash: Optional[ContentHash]
        type: Optional[Union[str, ContentSourceType]]
        value: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                hash: Optional[ContentHash] = ..., 
                type: Optional[Union[str, ContentSourceType]] = ..., 
                value: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        id: str
        name: str
        properties: Optional[CredentialProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CredentialProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.CredentialCreateOrUpdateParameters(_Model):
        name: str
        properties: CredentialCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: CredentialCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.CredentialCreateOrUpdateProperties(_Model):
        description: Optional[str]
        password: str
        user_name: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                password: str, 
                user_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.CredentialProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        last_modified_time: Optional[datetime]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.CredentialUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[CredentialUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[CredentialUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.CredentialUpdateProperties(_Model):
        description: Optional[str]
        password: Optional[str]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                password: Optional[str] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DeletedAutomationAccount(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[DeletedAutomationAccountProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[DeletedAutomationAccountProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DeletedAutomationAccountListResult(_Model):
        value: Optional[list[DeletedAutomationAccount]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[DeletedAutomationAccount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DeletedAutomationAccountProperties(_Model):
        automation_account_id: Optional[str]
        automation_account_resource_id: Optional[str]
        deletion_time: Optional[datetime]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                automation_account_id: Optional[str] = ..., 
                automation_account_resource_id: Optional[str] = ..., 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DeletedRunbook(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[DeletedRunbookProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[DeletedRunbookProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DeletedRunbookProperties(_Model):
        creation_time: Optional[datetime]
        deletion_time: Optional[datetime]
        runbook_id: Optional[str]
        runbook_type: Optional[str]
        runtime: Optional[str]
        runtime_environment: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                deletion_time: Optional[datetime] = ..., 
                runbook_id: Optional[str] = ..., 
                runbook_type: Optional[str] = ..., 
                runtime: Optional[str] = ..., 
                runtime_environment: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Dimension(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscConfiguration(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[DscConfigurationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str, 
                properties: Optional[DscConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DscConfigurationAssociationProperty(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscConfigurationCreateOrUpdateParameters(_Model):
        location: Optional[str]
        name: Optional[str]
        properties: DscConfigurationCreateOrUpdateProperties
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: DscConfigurationCreateOrUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DscConfigurationCreateOrUpdateProperties(_Model):
        description: Optional[str]
        log_progress: Optional[bool]
        log_verbose: Optional[bool]
        parameters: Optional[dict[str, DscConfigurationParameter]]
        source: ContentSource

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                parameters: Optional[dict[str, DscConfigurationParameter]] = ..., 
                source: ContentSource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscConfigurationParameter(_Model):
        default_value: Optional[str]
        is_mandatory: Optional[bool]
        position: Optional[int]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                is_mandatory: Optional[bool] = ..., 
                position: Optional[int] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscConfigurationProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        job_count: Optional[int]
        last_modified_time: Optional[datetime]
        log_verbose: Optional[bool]
        node_configuration_count: Optional[int]
        parameters: Optional[dict[str, DscConfigurationParameter]]
        provisioning_state: Optional[Literal["Succeeded"]]
        source: Optional[ContentSource]
        state: Optional[Union[str, DscConfigurationState]]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                job_count: Optional[int] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                log_verbose: Optional[bool] = ..., 
                node_configuration_count: Optional[int] = ..., 
                parameters: Optional[dict[str, DscConfigurationParameter]] = ..., 
                provisioning_state: Optional[Literal[Succeeded]] = ..., 
                source: Optional[ContentSource] = ..., 
                state: Optional[Union[str, DscConfigurationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDIT = "Edit"
        NEW = "New"
        PUBLISHED = "Published"


    class azure.mgmt.automation.models.DscConfigurationUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[DscConfigurationCreateOrUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[DscConfigurationCreateOrUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DscMetaConfiguration(_Model):
        action_after_reboot: Optional[str]
        allow_module_overwrite: Optional[bool]
        certificate_id: Optional[str]
        configuration_mode: Optional[str]
        configuration_mode_frequency_mins: Optional[int]
        reboot_node_if_needed: Optional[bool]
        refresh_frequency_mins: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action_after_reboot: Optional[str] = ..., 
                allow_module_overwrite: Optional[bool] = ..., 
                certificate_id: Optional[str] = ..., 
                configuration_mode: Optional[str] = ..., 
                configuration_mode_frequency_mins: Optional[int] = ..., 
                reboot_node_if_needed: Optional[bool] = ..., 
                refresh_frequency_mins: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNode(ProxyResource):
        id: str
        name: str
        properties: Optional[DscNodeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DscNodeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNodeConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[DscNodeConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DscNodeConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DscNodeConfigurationAssociationProperty(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNodeConfigurationCreateOrUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[DscNodeConfigurationCreateOrUpdateParametersProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[DscNodeConfigurationCreateOrUpdateParametersProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DscNodeConfigurationCreateOrUpdateParametersProperties(_Model):
        configuration: DscConfigurationAssociationProperty
        increment_node_configuration_build: Optional[bool]
        source: ContentSource

        @overload
        def __init__(
                self, 
                *, 
                configuration: DscConfigurationAssociationProperty, 
                increment_node_configuration_build: Optional[bool] = ..., 
                source: ContentSource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNodeConfigurationProperties(_Model):
        configuration: Optional[DscConfigurationAssociationProperty]
        creation_time: Optional[datetime]
        increment_node_configuration_build: Optional[bool]
        last_modified_time: Optional[datetime]
        node_count: Optional[int]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[DscConfigurationAssociationProperty] = ..., 
                creation_time: Optional[datetime] = ..., 
                increment_node_configuration_build: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                node_count: Optional[int] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNodeExtensionHandlerAssociationProperty(_Model):
        name: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNodeProperties(_Model):
        account_id: Optional[str]
        etag: Optional[str]
        extension_handler: Optional[list[DscNodeExtensionHandlerAssociationProperty]]
        ip: Optional[str]
        last_seen: Optional[datetime]
        node_configuration: Optional[DscNodeConfigurationAssociationProperty]
        node_id: Optional[str]
        registration_time: Optional[datetime]
        status: Optional[str]
        total_count: Optional[int]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                extension_handler: Optional[list[DscNodeExtensionHandlerAssociationProperty]] = ..., 
                ip: Optional[str] = ..., 
                last_seen: Optional[datetime] = ..., 
                node_configuration: Optional[DscNodeConfigurationAssociationProperty] = ..., 
                node_id: Optional[str] = ..., 
                registration_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                total_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DscNodeReport(_Model):
        configuration_version: Optional[str]
        end_time: Optional[datetime]
        errors: Optional[list[DscReportError]]
        host_name: Optional[str]
        i_pv4_addresses: Optional[list[str]]
        i_pv6_addresses: Optional[list[str]]
        id: Optional[str]
        last_modified_time: Optional[datetime]
        meta_configuration: Optional[DscMetaConfiguration]
        number_of_resources: Optional[int]
        raw_errors: Optional[str]
        reboot_requested: Optional[str]
        refresh_mode: Optional[str]
        report_format_version: Optional[str]
        report_id: Optional[str]
        resources: Optional[list[DscReportResource]]
        start_time: Optional[datetime]
        status: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration_version: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                errors: Optional[list[DscReportError]] = ..., 
                host_name: Optional[str] = ..., 
                i_pv4_addresses: Optional[list[str]] = ..., 
                i_pv6_addresses: Optional[list[str]] = ..., 
                id: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                meta_configuration: Optional[DscMetaConfiguration] = ..., 
                number_of_resources: Optional[int] = ..., 
                raw_errors: Optional[str] = ..., 
                reboot_requested: Optional[str] = ..., 
                refresh_mode: Optional[str] = ..., 
                report_format_version: Optional[str] = ..., 
                report_id: Optional[str] = ..., 
                resources: Optional[list[DscReportResource]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNodeUpdateParameters(_Model):
        node_id: Optional[str]
        properties: Optional[DscNodeUpdateParametersProperties]

        @overload
        def __init__(
                self, 
                *, 
                node_id: Optional[str] = ..., 
                properties: Optional[DscNodeUpdateParametersProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscNodeUpdateParametersProperties(_Model):
        node_configuration: Optional[DscNodeConfigurationAssociationProperty]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                node_configuration: Optional[DscNodeConfigurationAssociationProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.DscReportError(_Model):
        error_code: Optional[str]
        error_details: Optional[str]
        error_message: Optional[str]
        error_source: Optional[str]
        locale: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_details: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                error_source: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscReportResource(_Model):
        depends_on: Optional[list[DscReportResourceNavigation]]
        duration_in_seconds: Optional[float]
        error: Optional[str]
        module_name: Optional[str]
        module_version: Optional[str]
        resource_id: Optional[str]
        resource_name: Optional[str]
        source_info: Optional[str]
        start_date: Optional[datetime]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                depends_on: Optional[list[DscReportResourceNavigation]] = ..., 
                duration_in_seconds: Optional[float] = ..., 
                error: Optional[str] = ..., 
                module_name: Optional[str] = ..., 
                module_version: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                resource_name: Optional[str] = ..., 
                source_info: Optional[str] = ..., 
                start_date: Optional[datetime] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.DscReportResourceNavigation(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.EncryptionKeySourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_AUTOMATION = "Microsoft.Automation"
        MICROSOFT_KEYVAULT = "Microsoft.Keyvault"


    class azure.mgmt.automation.models.EncryptionProperties(_Model):
        identity: Optional[EncryptionPropertiesIdentity]
        key_source: Optional[Union[str, EncryptionKeySourceType]]
        key_vault_properties: Optional[KeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[EncryptionPropertiesIdentity] = ..., 
                key_source: Optional[Union[str, EncryptionKeySourceType]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.EncryptionPropertiesIdentity(_Model):
        user_assigned_identity: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.automation.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.automation.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.FieldDefinition(_Model):
        is_encrypted: Optional[bool]
        is_optional: Optional[bool]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                is_encrypted: Optional[bool] = ..., 
                is_optional: Optional[bool] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.GraphRunbookType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAPH_POWER_SHELL = "GraphPowerShell"
        GRAPH_POWER_SHELL_WORKFLOW = "GraphPowerShellWorkflow"


    class azure.mgmt.automation.models.GraphicalRunbookContent(_Model):
        graph_runbook_json: Optional[str]
        raw_content: Optional[RawGraphicalRunbookContent]

        @overload
        def __init__(
                self, 
                *, 
                graph_runbook_json: Optional[str] = ..., 
                raw_content: Optional[RawGraphicalRunbookContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.automation.models.HybridRunbookWorker(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[HybridRunbookWorkerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[HybridRunbookWorkerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerCreateOrUpdateParameters(_Model):
        vm_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                vm_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerCreateParameters(_Model):
        name: Optional[str]
        properties: Optional[HybridRunbookWorkerCreateOrUpdateParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HybridRunbookWorkerCreateOrUpdateParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[HybridRunbookWorkerGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[HybridRunbookWorkerGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerGroupCreateOrUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[HybridRunbookWorkerGroupCreateOrUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[HybridRunbookWorkerGroupCreateOrUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerGroupCreateOrUpdateProperties(_Model):
        credential: Optional[RunAsCredentialAssociationProperty]

        @overload
        def __init__(
                self, 
                *, 
                credential: Optional[RunAsCredentialAssociationProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerGroupProperties(_Model):
        credential: Optional[RunAsCredentialAssociationProperty]
        group_type: Optional[Union[str, GroupTypeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                credential: Optional[RunAsCredentialAssociationProperty] = ..., 
                group_type: Optional[Union[str, GroupTypeEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerMoveParameters(_Model):
        hybrid_runbook_worker_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                hybrid_runbook_worker_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.HybridRunbookWorkerProperties(_Model):
        ip: Optional[str]
        last_seen_date_time: Optional[datetime]
        registered_date_time: Optional[datetime]
        vm_resource_id: Optional[str]
        worker_name: Optional[str]
        worker_type: Optional[Union[str, WorkerType]]

        @overload
        def __init__(
                self, 
                *, 
                ip: Optional[str] = ..., 
                last_seen_date_time: Optional[datetime] = ..., 
                registered_date_time: Optional[datetime] = ..., 
                vm_resource_id: Optional[str] = ..., 
                worker_name: Optional[str] = ..., 
                worker_type: Optional[Union[str, WorkerType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesProperties]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Job(ProxyResource):
        id: str
        name: str
        properties: Optional[JobProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.JobCollectionItem(ProxyResource):
        id: str
        name: str
        properties: JobCollectionItemProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: JobCollectionItemProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.JobCollectionItemProperties(_Model):
        creation_time: Optional[datetime]
        end_time: Optional[datetime]
        job_id: Optional[str]
        job_runtime_environment: Optional[JobRuntimeEnvironment]
        last_modified_time: Optional[datetime]
        provisioning_state: Optional[str]
        run_on: Optional[str]
        runbook: Optional[RunbookAssociationProperty]
        start_time: Optional[datetime]
        started_by: Optional[str]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                job_runtime_environment: Optional[JobRuntimeEnvironment] = ..., 
                run_on: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.JobCreateParameters(_Model):
        properties: JobCreateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: JobCreateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.JobCreateProperties(_Model):
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]
        runbook: Optional[RunbookAssociationProperty]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.JobNavigation(_Model):
        id: Optional[str]


    class azure.mgmt.automation.models.JobProperties(_Model):
        creation_time: Optional[datetime]
        end_time: Optional[datetime]
        exception: Optional[str]
        job_id: Optional[str]
        job_runtime_environment: Optional[JobRuntimeEnvironment]
        last_modified_time: Optional[datetime]
        last_status_modified_time: Optional[datetime]
        parameters: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, JobProvisioningState]]
        run_on: Optional[str]
        runbook: Optional[RunbookAssociationProperty]
        start_time: Optional[datetime]
        started_by: Optional[str]
        status: Optional[Union[str, JobStatus]]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                end_time: Optional[datetime] = ..., 
                exception: Optional[str] = ..., 
                job_id: Optional[str] = ..., 
                job_runtime_environment: Optional[JobRuntimeEnvironment] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                last_status_modified_time: Optional[datetime] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                start_time: Optional[datetime] = ..., 
                started_by: Optional[str] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.JobProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PROCESSING = "Processing"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"


    class azure.mgmt.automation.models.JobRuntimeEnvironment(_Model):
        runtime_environment_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                runtime_environment_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.JobSchedule(ProxyResource):
        id: str
        name: str
        properties: Optional[JobScheduleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[JobScheduleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.JobScheduleCreateParameters(_Model):
        properties: JobScheduleCreateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: JobScheduleCreateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.JobScheduleCreateProperties(_Model):
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]
        runbook: RunbookAssociationProperty
        schedule: ScheduleAssociationProperty

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: RunbookAssociationProperty, 
                schedule: ScheduleAssociationProperty
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.JobScheduleProperties(_Model):
        job_schedule_id: Optional[str]
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]
        runbook: Optional[RunbookAssociationProperty]
        schedule: Optional[ScheduleAssociationProperty]

        @overload
        def __init__(
                self, 
                *, 
                job_schedule_id: Optional[str] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                schedule: Optional[ScheduleAssociationProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.automation.models.JobStream(_Model):
        id: Optional[str]
        properties: Optional[JobStreamProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[JobStreamProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.JobStreamProperties(_Model):
        job_stream_id: Optional[str]
        stream_text: Optional[str]
        stream_type: Optional[Union[str, JobStreamType]]
        summary: Optional[str]
        time: Optional[datetime]
        value: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                job_stream_id: Optional[str] = ..., 
                stream_text: Optional[str] = ..., 
                stream_type: Optional[Union[str, JobStreamType]] = ..., 
                summary: Optional[str] = ..., 
                time: Optional[datetime] = ..., 
                value: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.JobStreamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        DEBUG = "Debug"
        ERROR = "Error"
        OUTPUT = "Output"
        PROGRESS = "Progress"
        VERBOSE = "Verbose"
        WARNING = "Warning"


    class azure.mgmt.automation.models.Key(_Model):
        key_name: Optional[Union[str, AutomationKeyName]]
        permissions: Optional[Union[str, AutomationKeyPermissions]]
        value: Optional[str]


    class azure.mgmt.automation.models.KeyListResult(_Model):
        keys_property: Optional[list[Key]]

        @overload
        def __init__(
                self, 
                *, 
                keys_property: Optional[list[Key]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.KeyVaultProperties(_Model):
        key_name: Optional[str]
        key_version: Optional[str]
        keyvault_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                keyvault_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.LinkedWorkspace(_Model):
        id: Optional[str]


    class azure.mgmt.automation.models.LinuxProperties(_Model):
        excluded_package_name_masks: Optional[list[str]]
        included_package_classifications: Optional[Union[str, LinuxUpdateClasses]]
        included_package_name_masks: Optional[list[str]]
        reboot_setting: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                excluded_package_name_masks: Optional[list[str]] = ..., 
                included_package_classifications: Optional[Union[str, LinuxUpdateClasses]] = ..., 
                included_package_name_masks: Optional[list[str]] = ..., 
                reboot_setting: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.LinuxUpdateClasses(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        OTHER = "Other"
        SECURITY = "Security"
        UNCLASSIFIED = "Unclassified"


    class azure.mgmt.automation.models.LogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        dimensions: Optional[list[Dimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        name: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[list[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Module(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[ModuleProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str, 
                properties: Optional[ModuleProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ModuleCreateOrUpdateParameters(_Model):
        location: Optional[str]
        name: Optional[str]
        properties: ModuleCreateOrUpdateProperties
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: ModuleCreateOrUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ModuleCreateOrUpdateProperties(_Model):
        content_link: ContentLink

        @overload
        def __init__(
                self, 
                *, 
                content_link: ContentLink
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ModuleErrorInfo(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ModuleProperties(_Model):
        activity_count: Optional[int]
        content_link: Optional[ContentLink]
        creation_time: Optional[datetime]
        description: Optional[str]
        error: Optional[ModuleErrorInfo]
        is_composite: Optional[bool]
        is_global: Optional[bool]
        last_modified_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ModuleProvisioningState]]
        size_in_bytes: Optional[int]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activity_count: Optional[int] = ..., 
                content_link: Optional[ContentLink] = ..., 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                error: Optional[ModuleErrorInfo] = ..., 
                is_composite: Optional[bool] = ..., 
                is_global: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                provisioning_state: Optional[Union[str, ModuleProvisioningState]] = ..., 
                size_in_bytes: Optional[int] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ModuleProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITIES_STORED = "ActivitiesStored"
        CANCELED = "Canceled"
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


    class azure.mgmt.automation.models.ModuleUpdateParameters(_Model):
        location: Optional[str]
        name: Optional[str]
        properties: Optional[ModuleUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ModuleUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ModuleUpdateProperties(_Model):
        content_link: Optional[ContentLink]

        @overload
        def __init__(
                self, 
                *, 
                content_link: Optional[ContentLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.NodeCount(_Model):
        name: Optional[str]
        properties: Optional[NodeCountProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[NodeCountProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.NodeCountProperties(_Model):
        count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.NodeCounts(_Model):
        total_count: Optional[int]
        value: Optional[list[NodeCount]]

        @overload
        def __init__(
                self, 
                *, 
                total_count: Optional[int] = ..., 
                value: Optional[list[NodeCount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.NonAzureQueryProperties(_Model):
        function_alias: Optional[str]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                function_alias: Optional[str] = ..., 
                workspace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.OperatingSystemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.automation.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationPropertiesFormat]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationPropertiesFormat] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.OperationPropertiesFormat(_Model):
        service_specification: Optional[OperationPropertiesFormatServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[OperationPropertiesFormatServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.OperationPropertiesFormatServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Package(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PackageProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PackageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.PackageCreateOrUpdateParameters(_Model):
        all_of: Optional[TrackedResource]
        properties: PackageCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                all_of: Optional[TrackedResource] = ..., 
                properties: PackageCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.PackageCreateOrUpdateProperties(_Model):
        content_link: ContentLink

        @overload
        def __init__(
                self, 
                *, 
                content_link: ContentLink
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.PackageErrorInfo(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.PackageProperties(_Model):
        all_of: Optional[SystemData]
        content_link: Optional[ContentLink]
        default: Optional[bool]
        error: Optional[PackageErrorInfo]
        provisioning_state: Optional[Union[str, PackageProvisioningState]]
        size_in_bytes: Optional[int]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                all_of: Optional[SystemData] = ..., 
                content_link: Optional[ContentLink] = ..., 
                default: Optional[bool] = ..., 
                error: Optional[PackageErrorInfo] = ..., 
                size_in_bytes: Optional[int] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.PackageProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITIES_STORED = "ActivitiesStored"
        CANCELED = "Canceled"
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


    class azure.mgmt.automation.models.PackageUpdateParameters(_Model):
        all_of: Optional[TrackedResource]
        properties: Optional[PackageUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                all_of: Optional[TrackedResource] = ..., 
                properties: Optional[PackageUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.PackageUpdateProperties(_Model):
        content_link: Optional[ContentLink]

        @overload
        def __init__(
                self, 
                *, 
                content_link: Optional[ContentLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpointProperty]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpointProperty] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionStateProperty] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.PrivateEndpointProperty(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]


    class azure.mgmt.automation.models.PrivateLinkServiceConnectionStateProperty(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        RUNNING = "Running"


    class azure.mgmt.automation.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.automation.models.PythonPackageCreateParameters(_Model):
        properties: PythonPackageCreateProperties
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: PythonPackageCreateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.PythonPackageCreateProperties(_Model):
        content_link: ContentLink

        @overload
        def __init__(
                self, 
                *, 
                content_link: ContentLink
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.PythonPackageUpdateParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RawGraphicalRunbookContent(_Model):
        runbook_definition: Optional[str]
        runbook_type: Optional[Union[str, GraphRunbookType]]
        schema_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                runbook_definition: Optional[str] = ..., 
                runbook_type: Optional[Union[str, GraphRunbookType]] = ..., 
                schema_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.automation.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.automation.models.RunAsCredentialAssociationProperty(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Runbook(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[RunbookProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str, 
                properties: Optional[RunbookProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.RunbookAssociationProperty(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RunbookCreateOrUpdateParameters(_Model):
        location: Optional[str]
        name: Optional[str]
        properties: RunbookCreateOrUpdateProperties
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: RunbookCreateOrUpdateProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.RunbookCreateOrUpdateProperties(_Model):
        description: Optional[str]
        draft: Optional[RunbookDraft]
        log_activity_trace: Optional[int]
        log_progress: Optional[bool]
        log_verbose: Optional[bool]
        publish_content_link: Optional[ContentLink]
        runbook_type: Union[str, RunbookTypeEnum]
        runtime_environment: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                draft: Optional[RunbookDraft] = ..., 
                log_activity_trace: Optional[int] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                publish_content_link: Optional[ContentLink] = ..., 
                runbook_type: Union[str, RunbookTypeEnum], 
                runtime_environment: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RunbookDraft(_Model):
        creation_time: Optional[datetime]
        draft_content_link: Optional[ContentLink]
        in_edit: Optional[bool]
        last_modified_time: Optional[datetime]
        output_types: Optional[list[str]]
        parameters: Optional[dict[str, RunbookParameter]]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                draft_content_link: Optional[ContentLink] = ..., 
                in_edit: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                output_types: Optional[list[str]] = ..., 
                parameters: Optional[dict[str, RunbookParameter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RunbookDraftUndoEditResult(_Model):
        request_id: Optional[str]
        status_code: Optional[Union[str, HttpStatusCode]]

        @overload
        def __init__(
                self, 
                *, 
                request_id: Optional[str] = ..., 
                status_code: Optional[Union[str, HttpStatusCode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RunbookParameter(_Model):
        default_value: Optional[str]
        is_mandatory: Optional[bool]
        position: Optional[int]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                is_mandatory: Optional[bool] = ..., 
                position: Optional[int] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RunbookProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        draft: Optional[RunbookDraft]
        job_count: Optional[int]
        last_modified_by: Optional[str]
        last_modified_time: Optional[datetime]
        log_activity_trace: Optional[int]
        log_progress: Optional[bool]
        log_verbose: Optional[bool]
        output_types: Optional[list[str]]
        parameters: Optional[dict[str, RunbookParameter]]
        provisioning_state: Optional[Literal["Succeeded"]]
        publish_content_link: Optional[ContentLink]
        runbook_type: Optional[Union[str, RunbookTypeEnum]]
        runtime_environment: Optional[str]
        state: Optional[Union[str, RunbookState]]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                draft: Optional[RunbookDraft] = ..., 
                job_count: Optional[int] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                log_activity_trace: Optional[int] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ..., 
                output_types: Optional[list[str]] = ..., 
                parameters: Optional[dict[str, RunbookParameter]] = ..., 
                provisioning_state: Optional[Literal[Succeeded]] = ..., 
                publish_content_link: Optional[ContentLink] = ..., 
                runbook_type: Optional[Union[str, RunbookTypeEnum]] = ..., 
                runtime_environment: Optional[str] = ..., 
                state: Optional[Union[str, RunbookState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RunbookState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDIT = "Edit"
        NEW = "New"
        PUBLISHED = "Published"


    class azure.mgmt.automation.models.RunbookTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAPH = "Graph"
        GRAPH_POWER_SHELL = "GraphPowerShell"
        GRAPH_POWER_SHELL_WORKFLOW = "GraphPowerShellWorkflow"
        POWER_SHELL = "PowerShell"
        POWER_SHELL72 = "PowerShell72"
        POWER_SHELL_WORKFLOW = "PowerShellWorkflow"
        PYTHON = "Python"
        PYTHON2 = "Python2"
        PYTHON3 = "Python3"
        SCRIPT = "Script"


    class azure.mgmt.automation.models.RunbookUpdateParameters(_Model):
        location: Optional[str]
        name: Optional[str]
        properties: Optional[RunbookUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[RunbookUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.RunbookUpdateProperties(_Model):
        description: Optional[str]
        log_activity_trace: Optional[int]
        log_progress: Optional[bool]
        log_verbose: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                log_activity_trace: Optional[int] = ..., 
                log_progress: Optional[bool] = ..., 
                log_verbose: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RuntimeEnvironment(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[RuntimeEnvironmentProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[RuntimeEnvironmentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RuntimeEnvironmentProperties(_Model):
        default_packages: Optional[dict[str, str]]
        description: Optional[str]
        runtime: Optional[RuntimeProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                default_packages: Optional[dict[str, str]] = ..., 
                description: Optional[str] = ..., 
                runtime: Optional[RuntimeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.RuntimeEnvironmentUpdateParameters(_Model):
        properties: Optional[RuntimeEnvironmentUpdateProperties]
        system_data: Optional[SystemData]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuntimeEnvironmentUpdateProperties] = ..., 
                system_data: Optional[SystemData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.RuntimeEnvironmentUpdateProperties(_Model):
        default_packages: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                default_packages: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.RuntimeProperties(_Model):
        language: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SUCScheduleProperties(_Model):
        advanced_schedule: Optional[AdvancedSchedule]
        creation_time: Optional[datetime]
        description: Optional[str]
        expiry_time: Optional[datetime]
        expiry_time_offset_minutes: Optional[float]
        frequency: Optional[Union[str, ScheduleFrequency]]
        interval: Optional[int]
        is_enabled: Optional[bool]
        last_modified_time: Optional[datetime]
        next_run: Optional[datetime]
        next_run_offset_minutes: Optional[float]
        start_time: Optional[datetime]
        start_time_offset_minutes: Optional[float]
        time_zone: Optional[str]

        @overload
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
                is_enabled: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                next_run: Optional[datetime] = ..., 
                next_run_offset_minutes: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Schedule(ProxyResource):
        id: str
        name: str
        properties: Optional[ScheduleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ScheduleAssociationProperty(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ScheduleCreateOrUpdateParameters(_Model):
        name: str
        properties: ScheduleCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: ScheduleCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ScheduleCreateOrUpdateProperties(_Model):
        advanced_schedule: Optional[AdvancedSchedule]
        description: Optional[str]
        expiry_time: Optional[datetime]
        frequency: Union[str, ScheduleFrequency]
        interval: Optional[Any]
        start_time: datetime
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                advanced_schedule: Optional[AdvancedSchedule] = ..., 
                description: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                frequency: Union[str, ScheduleFrequency], 
                interval: Optional[Any] = ..., 
                start_time: datetime, 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.automation.models.ScheduleProperties(_Model):
        advanced_schedule: Optional[AdvancedSchedule]
        creation_time: Optional[datetime]
        description: Optional[str]
        expiry_time: Optional[datetime]
        expiry_time_offset_minutes: Optional[float]
        frequency: Optional[Union[str, ScheduleFrequency]]
        interval: Optional[Any]
        is_enabled: Optional[bool]
        last_modified_time: Optional[datetime]
        next_run: Optional[datetime]
        next_run_offset_minutes: Optional[float]
        start_time: Optional[datetime]
        start_time_offset_minutes: Optional[float]
        time_zone: Optional[str]

        @overload
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
                is_enabled: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                next_run: Optional[datetime] = ..., 
                next_run_offset_minutes: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.ScheduleUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[ScheduleUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[ScheduleUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.ScheduleUpdateProperties(_Model):
        description: Optional[str]
        is_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: Union[str, SkuNameEnum]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Union[str, SkuNameEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SkuNameEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"


    class azure.mgmt.automation.models.SoftwareUpdateConfiguration(ProxyResource):
        id: str
        name: str
        properties: SoftwareUpdateConfigurationProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SoftwareUpdateConfigurationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationCollectionItem(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: SoftwareUpdateConfigurationCollectionItemProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SoftwareUpdateConfigurationCollectionItemProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationCollectionItemProperties(_Model):
        creation_time: Optional[datetime]
        frequency: Optional[Union[str, ScheduleFrequency]]
        last_modified_time: Optional[datetime]
        next_run: Optional[datetime]
        provisioning_state: Optional[str]
        start_time: Optional[datetime]
        tasks: Optional[SoftwareUpdateConfigurationTasks]
        update_configuration: Optional[UpdateConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduleFrequency]] = ..., 
                next_run: Optional[datetime] = ..., 
                start_time: Optional[datetime] = ..., 
                tasks: Optional[SoftwareUpdateConfigurationTasks] = ..., 
                update_configuration: Optional[UpdateConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationListResult(_Model):
        value: Optional[list[SoftwareUpdateConfigurationCollectionItem]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SoftwareUpdateConfigurationCollectionItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationMachineRun(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[UpdateConfigurationMachineRunProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateConfigurationMachineRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationMachineRunListResult(_Model):
        next_link: Optional[str]
        value: list[SoftwareUpdateConfigurationMachineRun]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[SoftwareUpdateConfigurationMachineRun]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationProperties(_Model):
        created_by: Optional[str]
        creation_time: Optional[datetime]
        error: Optional[AutomationErrorResponse]
        last_modified_by: Optional[str]
        last_modified_time: Optional[datetime]
        provisioning_state: Optional[str]
        schedule_info: SUCScheduleProperties
        tasks: Optional[SoftwareUpdateConfigurationTasks]
        update_configuration: UpdateConfiguration

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[AutomationErrorResponse] = ..., 
                schedule_info: SUCScheduleProperties, 
                tasks: Optional[SoftwareUpdateConfigurationTasks] = ..., 
                update_configuration: UpdateConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRun(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[SoftwareUpdateConfigurationRunProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SoftwareUpdateConfigurationRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRunListResult(_Model):
        next_link: Optional[str]
        value: list[SoftwareUpdateConfigurationRun]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[SoftwareUpdateConfigurationRun]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRunProperties(_Model):
        computer_count: Optional[int]
        configured_duration: Optional[str]
        created_by: Optional[str]
        creation_time: Optional[datetime]
        end_time: Optional[datetime]
        failed_count: Optional[int]
        last_modified_by: Optional[str]
        last_modified_time: Optional[datetime]
        os_type: Optional[str]
        software_update_configuration: Optional[UpdateConfigurationNavigation]
        start_time: Optional[datetime]
        status: Optional[str]
        tasks: Optional[SoftwareUpdateConfigurationRunTasks]

        @overload
        def __init__(
                self, 
                *, 
                software_update_configuration: Optional[UpdateConfigurationNavigation] = ..., 
                tasks: Optional[SoftwareUpdateConfigurationRunTasks] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRunTaskProperties(_Model):
        job_id: Optional[str]
        source: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ..., 
                source: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationRunTasks(_Model):
        post_task: Optional[SoftwareUpdateConfigurationRunTaskProperties]
        pre_task: Optional[SoftwareUpdateConfigurationRunTaskProperties]

        @overload
        def __init__(
                self, 
                *, 
                post_task: Optional[SoftwareUpdateConfigurationRunTaskProperties] = ..., 
                pre_task: Optional[SoftwareUpdateConfigurationRunTaskProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SoftwareUpdateConfigurationTasks(_Model):
        post_task: Optional[TaskProperties]
        pre_task: Optional[TaskProperties]

        @overload
        def __init__(
                self, 
                *, 
                post_task: Optional[TaskProperties] = ..., 
                pre_task: Optional[TaskProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControl(ProxyResource):
        id: str
        name: str
        properties: Optional[SourceControlProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SourceControlProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlCreateOrUpdateParameters(_Model):
        properties: SourceControlCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SourceControlCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlCreateOrUpdateProperties(_Model):
        auto_sync: Optional[bool]
        branch: Optional[str]
        description: Optional[str]
        folder_path: Optional[str]
        publish_runbook: Optional[bool]
        repo_url: Optional[str]
        security_token: Optional[SourceControlSecurityTokenProperties]
        source_type: Optional[Union[str, SourceType]]

        @overload
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
                source_type: Optional[Union[str, SourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlProperties(_Model):
        auto_sync: Optional[bool]
        branch: Optional[str]
        creation_time: Optional[datetime]
        description: Optional[str]
        folder_path: Optional[str]
        last_modified_time: Optional[datetime]
        publish_runbook: Optional[bool]
        repo_url: Optional[str]
        source_type: Optional[Union[str, SourceType]]

        @overload
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
                source_type: Optional[Union[str, SourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlSecurityTokenProperties(_Model):
        access_token: Optional[str]
        refresh_token: Optional[str]
        token_type: Optional[Union[str, TokenType]]

        @overload
        def __init__(
                self, 
                *, 
                access_token: Optional[str] = ..., 
                refresh_token: Optional[str] = ..., 
                token_type: Optional[Union[str, TokenType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJob(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[SourceControlSyncJobProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SourceControlSyncJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobById(_Model):
        id: Optional[str]
        properties: Optional[SourceControlSyncJobByIdProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[SourceControlSyncJobByIdProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobByIdProperties(_Model):
        creation_time: Optional[datetime]
        end_time: Optional[datetime]
        exception: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_control_sync_job_id: Optional[str]
        start_time: Optional[datetime]
        sync_type: Optional[Union[str, SyncType]]

        @overload
        def __init__(
                self, 
                *, 
                exception: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                source_control_sync_job_id: Optional[str] = ..., 
                sync_type: Optional[Union[str, SyncType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobCreateParameters(_Model):
        properties: SourceControlSyncJobCreateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SourceControlSyncJobCreateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobCreateProperties(_Model):
        commit_id: str

        @overload
        def __init__(
                self, 
                *, 
                commit_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobProperties(_Model):
        creation_time: Optional[datetime]
        end_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_control_sync_job_id: Optional[str]
        start_time: Optional[datetime]
        sync_type: Optional[Union[str, SyncType]]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                source_control_sync_job_id: Optional[str] = ..., 
                sync_type: Optional[Union[str, SyncType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobStream(_Model):
        id: Optional[str]
        properties: Optional[SourceControlSyncJobStreamProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SourceControlSyncJobStreamProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobStreamById(_Model):
        id: Optional[str]
        properties: Optional[SourceControlSyncJobStreamByIdProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SourceControlSyncJobStreamByIdProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobStreamByIdProperties(_Model):
        source_control_sync_job_stream_id: Optional[str]
        stream_text: Optional[str]
        stream_type: Optional[Union[str, StreamType]]
        summary: Optional[str]
        time: Optional[datetime]
        value: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                source_control_sync_job_stream_id: Optional[str] = ..., 
                stream_text: Optional[str] = ..., 
                stream_type: Optional[Union[str, StreamType]] = ..., 
                summary: Optional[str] = ..., 
                value: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlSyncJobStreamProperties(_Model):
        source_control_sync_job_stream_id: Optional[str]
        stream_type: Optional[Union[str, StreamType]]
        summary: Optional[str]
        time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                source_control_sync_job_stream_id: Optional[str] = ..., 
                stream_type: Optional[Union[str, StreamType]] = ..., 
                summary: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceControlUpdateParameters(_Model):
        properties: Optional[SourceControlUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SourceControlUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.SourceControlUpdateProperties(_Model):
        auto_sync: Optional[bool]
        branch: Optional[str]
        description: Optional[str]
        folder_path: Optional[str]
        publish_runbook: Optional[bool]
        security_token: Optional[SourceControlSecurityTokenProperties]

        @overload
        def __init__(
                self, 
                *, 
                auto_sync: Optional[bool] = ..., 
                branch: Optional[str] = ..., 
                description: Optional[str] = ..., 
                folder_path: Optional[str] = ..., 
                publish_runbook: Optional[bool] = ..., 
                security_token: Optional[SourceControlSecurityTokenProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GIT_HUB = "GitHub"
        VSO_GIT = "VsoGit"
        VSO_TFVC = "VsoTfvc"


    class azure.mgmt.automation.models.Statistics(_Model):
        counter_property: Optional[str]
        counter_value: Optional[int]
        end_time: Optional[datetime]
        id: Optional[str]
        start_time: Optional[datetime]


    class azure.mgmt.automation.models.StreamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        OUTPUT = "Output"


    class azure.mgmt.automation.models.SyncType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_SYNC = "FullSync"
        PARTIAL_SYNC = "PartialSync"


    class azure.mgmt.automation.models.SystemData(_Model):
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


    class azure.mgmt.automation.models.TagOperators(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ANY = "Any"


    class azure.mgmt.automation.models.TagSettingsProperties(_Model):
        filter_operator: Optional[Union[str, TagOperators]]
        tags: Optional[dict[str, list[str]]]

        @overload
        def __init__(
                self, 
                *, 
                filter_operator: Optional[Union[str, TagOperators]] = ..., 
                tags: Optional[dict[str, list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.TargetProperties(_Model):
        azure_queries: Optional[list[AzureQueryProperties]]
        non_azure_queries: Optional[list[NonAzureQueryProperties]]

        @overload
        def __init__(
                self, 
                *, 
                azure_queries: Optional[list[AzureQueryProperties]] = ..., 
                non_azure_queries: Optional[list[NonAzureQueryProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.TaskProperties(_Model):
        parameters: Optional[dict[str, str]]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.TestJob(_Model):
        creation_time: Optional[datetime]
        end_time: Optional[datetime]
        exception: Optional[str]
        last_modified_time: Optional[datetime]
        last_status_modified_time: Optional[datetime]
        log_activity_trace: Optional[int]
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]
        start_time: Optional[datetime]
        status: Optional[str]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                end_time: Optional[datetime] = ..., 
                exception: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                last_status_modified_time: Optional[datetime] = ..., 
                log_activity_trace: Optional[int] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.TestJobCreateParameters(_Model):
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]
        runtime_environment: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runtime_environment: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.TokenType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OAUTH = "Oauth"
        PERSONAL_ACCESS_TOKEN = "PersonalAccessToken"


    class azure.mgmt.automation.models.TrackedResource(Resource):
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


    class azure.mgmt.automation.models.TypeField(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.UpdateConfiguration(_Model):
        azure_virtual_machines: Optional[list[str]]
        duration: Optional[timedelta]
        linux: Optional[LinuxProperties]
        non_azure_computer_names: Optional[list[str]]
        operating_system: Union[str, OperatingSystemType]
        targets: Optional[TargetProperties]
        windows: Optional[WindowsProperties]

        @overload
        def __init__(
                self, 
                *, 
                azure_virtual_machines: Optional[list[str]] = ..., 
                duration: Optional[timedelta] = ..., 
                linux: Optional[LinuxProperties] = ..., 
                non_azure_computer_names: Optional[list[str]] = ..., 
                operating_system: Union[str, OperatingSystemType], 
                targets: Optional[TargetProperties] = ..., 
                windows: Optional[WindowsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.UpdateConfigurationMachineRunProperties(_Model):
        configured_duration: Optional[str]
        correlation_id: Optional[str]
        created_by: Optional[str]
        creation_time: Optional[datetime]
        end_time: Optional[datetime]
        error: Optional[AutomationErrorResponse]
        job: Optional[JobNavigation]
        last_modified_by: Optional[str]
        last_modified_time: Optional[datetime]
        os_type: Optional[str]
        software_update_configuration: Optional[UpdateConfigurationNavigation]
        source_computer_id: Optional[str]
        start_time: Optional[datetime]
        status: Optional[str]
        target_computer: Optional[str]
        target_computer_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[AutomationErrorResponse] = ..., 
                job: Optional[JobNavigation] = ..., 
                software_update_configuration: Optional[UpdateConfigurationNavigation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.UpdateConfigurationNavigation(_Model):
        name: Optional[str]


    class azure.mgmt.automation.models.Usage(_Model):
        current_value: Optional[float]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[UsageCounterName]
        throttle_status: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[float] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[UsageCounterName] = ..., 
                throttle_status: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.UsageCounterName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.UserAssignedIdentitiesProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.automation.models.Variable(ProxyResource):
        id: str
        name: str
        properties: Optional[VariableProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VariableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.VariableCreateOrUpdateParameters(_Model):
        name: str
        properties: VariableCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: VariableCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.VariableCreateOrUpdateProperties(_Model):
        description: Optional[str]
        is_encrypted: Optional[bool]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_encrypted: Optional[bool] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.VariableProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        is_encrypted: Optional[bool]
        last_modified_time: Optional[datetime]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                is_encrypted: Optional[bool] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.VariableUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[VariableUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[VariableUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.VariableUpdateProperties(_Model):
        description: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Watcher(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[WatcherProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[WatcherProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.WatcherProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        execution_frequency_in_seconds: Optional[int]
        last_modified_by: Optional[str]
        last_modified_time: Optional[datetime]
        script_name: Optional[str]
        script_parameters: Optional[dict[str, str]]
        script_run_on: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                execution_frequency_in_seconds: Optional[int] = ..., 
                script_name: Optional[str] = ..., 
                script_parameters: Optional[dict[str, str]] = ..., 
                script_run_on: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.WatcherUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[WatcherUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[WatcherUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.WatcherUpdateProperties(_Model):
        execution_frequency_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                execution_frequency_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.Webhook(ProxyResource):
        id: str
        name: str
        properties: Optional[WebhookProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WebhookProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.WebhookCreateOrUpdateParameters(_Model):
        name: str
        properties: WebhookCreateOrUpdateProperties

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: WebhookCreateOrUpdateProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.WebhookCreateOrUpdateProperties(_Model):
        expiry_time: Optional[datetime]
        is_enabled: Optional[bool]
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]
        runbook: Optional[RunbookAssociationProperty]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[datetime] = ..., 
                is_enabled: Optional[bool] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.WebhookProperties(_Model):
        creation_time: Optional[datetime]
        description: Optional[str]
        expiry_time: Optional[datetime]
        is_enabled: Optional[bool]
        last_invoked_time: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_time: Optional[datetime]
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]
        runbook: Optional[RunbookAssociationProperty]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_enabled: Optional[bool] = ..., 
                last_invoked_time: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ..., 
                runbook: Optional[RunbookAssociationProperty] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.WebhookUpdateParameters(_Model):
        name: Optional[str]
        properties: Optional[WebhookUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[WebhookUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.automation.models.WebhookUpdateProperties(_Model):
        description: Optional[str]
        is_enabled: Optional[bool]
        parameters: Optional[dict[str, str]]
        run_on: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                parameters: Optional[dict[str, str]] = ..., 
                run_on: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.automation.models.WindowsProperties(_Model):
        excluded_kb_numbers: Optional[list[str]]
        included_kb_numbers: Optional[list[str]]
        included_update_classifications: Optional[Union[str, WindowsUpdateClasses]]
        reboot_setting: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                excluded_kb_numbers: Optional[list[str]] = ..., 
                included_kb_numbers: Optional[list[str]] = ..., 
                included_update_classifications: Optional[Union[str, WindowsUpdateClasses]] = ..., 
                reboot_setting: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
            ) -> None: ...

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
            ) -> ItemPaged[Activity]: ...


    class azure.mgmt.automation.operations.AgentRegistrationInformationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> None: ...

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
        def list(self, **kwargs: Any) -> ItemPaged[AutomationAccount]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AutomationAccount]: ...

        @distributed_trace
        def list_deleted_runbooks(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DeletedRunbook]: ...

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


    class azure.mgmt.automation.operations.CertificateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Certificate]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[Connection]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[ConnectionType]: ...


    class azure.mgmt.automation.operations.CredentialOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Credential]: ...

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
            ) -> None: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> DeletedAutomationAccountListResult: ...


    class azure.mgmt.automation.operations.DscConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
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
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                inlinecount: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DscConfiguration]: ...

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
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DscConfiguration: ...


    class azure.mgmt.automation.operations.DscNodeConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                inlinecount: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DscNodeConfiguration]: ...


    class azure.mgmt.automation.operations.DscNodeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                inlinecount: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DscNode]: ...

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
            ) -> None: ...

        @distributed_trace
        def list_by_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                module_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TypeField]: ...


    class azure.mgmt.automation.operations.HybridRunbookWorkerGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[HybridRunbookWorkerGroup]: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[HybridRunbookWorker]: ...

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

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: Optional[HybridRunbookWorkerCreateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: Optional[HybridRunbookWorkerCreateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                hybrid_runbook_worker_group_name: str, 
                hybrid_runbook_worker_id: str, 
                hybrid_runbook_worker_creation_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HybridRunbookWorker: ...


    class azure.mgmt.automation.operations.JobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                parameters: JobCreateParameters, 
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                parameters: JobCreateParameters, 
                *, 
                client_request_id: Optional[str] = ..., 
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
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> Job: ...

        @distributed_trace
        def get_output(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def get_runbook_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobCollectionItem]: ...

        @distributed_trace
        def resume(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def suspend(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.automation.operations.JobScheduleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobSchedule]: ...


    class azure.mgmt.automation.operations.JobStreamOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                job_stream_id: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JobStream: ...

        @distributed_trace
        def list_by_job(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                job_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobStream]: ...


    class azure.mgmt.automation.operations.KeysOperations:

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
            ) -> KeyListResult: ...


    class azure.mgmt.automation.operations.LinkedWorkspaceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[Module]: ...

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
            ) -> None: ...

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
            ) -> None: ...

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
            ) -> str: ...

        @distributed_trace
        def list_by_node(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                node_id: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DscNodeReport]: ...


    class azure.mgmt.automation.operations.ObjectDataTypesOperations:

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
            ) -> ItemPaged[TypeField]: ...

        @distributed_trace
        def list_fields_by_type(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                type_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TypeField]: ...


    class azure.mgmt.automation.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.automation.operations.PackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                **kwargs: Any
            ) -> Package: ...

        @distributed_trace
        def list_by_runtime_environment(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Package]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: PackageUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                package_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Package: ...


    class azure.mgmt.automation.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.automation.operations.PrivateLinkResourcesOperations:

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
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.automation.operations.Python2PackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Module]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[Module]: ...

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
            ) -> None: ...

        @distributed_trace
        def begin_replace_content(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runbook_name: str, 
                runbook_content: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

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
            ) -> str: ...

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
            ) -> None: ...

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
            ) -> str: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Runbook]: ...

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


    class azure.mgmt.automation.operations.RuntimeEnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: RuntimeEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: RuntimeEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @distributed_trace
        def list_by_automation_account(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RuntimeEnvironment]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: RuntimeEnvironmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: RuntimeEnvironmentUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                runtime_environment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RuntimeEnvironment: ...


    class azure.mgmt.automation.operations.ScheduleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Schedule]: ...

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
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_machine_run_id: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationMachineRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationMachineRunListResult: ...


    class azure.mgmt.automation.operations.SoftwareUpdateConfigurationRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_id(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_run_id: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationRunListResult: ...


    class azure.mgmt.automation.operations.SoftwareUpdateConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                parameters: SoftwareUpdateConfiguration, 
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                parameters: SoftwareUpdateConfiguration, 
                *, 
                client_request_id: Optional[str] = ..., 
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
                *, 
                client_request_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_name(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                software_update_configuration_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                automation_account_name: str, 
                *, 
                client_request_id: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> SoftwareUpdateConfigurationListResult: ...


    class azure.mgmt.automation.operations.SourceControlOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SourceControl]: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SourceControlSyncJob]: ...


    class azure.mgmt.automation.operations.SourceControlSyncJobStreamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SourceControlSyncJobStream]: ...


    class azure.mgmt.automation.operations.StatisticsOperations:

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Statistics]: ...


    class azure.mgmt.automation.operations.TestJobOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[JobStream]: ...


    class azure.mgmt.automation.operations.UsagesOperations:

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
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.automation.operations.VariableOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Variable]: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Watcher]: ...

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
            ) -> None: ...

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
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Webhook]: ...

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


namespace azure.mgmt.automation.types

    class azure.mgmt.automation.types.AdvancedSchedule(TypedDict, total=False):
        monthDays: list[int]
        month_days: list[int]
        monthlyOccurrences: list[AdvancedScheduleMonthlyOccurrence]
        monthly_occurrences: list[AdvancedScheduleMonthlyOccurrence]
        weekDays: list[str]
        week_days: list[str]


    class azure.mgmt.automation.types.AdvancedScheduleMonthlyOccurrence(TypedDict, total=False):
        key "day": Union[str, ScheduleDay]
        key "occurrence": int
        day: Union[str, ScheduleDay]
        occurrence: int


    class azure.mgmt.automation.types.AgentRegistrationRegenerateKeyParameter(TypedDict, total=False):
        key "keyName": Required[Union[str, AgentRegistrationKeyName]]
        key_name: Union[str, AgentRegistrationKeyName]


    class azure.mgmt.automation.types.AutomationAccountCreateOrUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('AutomationAccountCreateOrUpdateProperties', module='types')
        identity: Identity
        location: str
        name: str
        properties: AutomationAccountCreateOrUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.AutomationAccountCreateOrUpdateProperties(TypedDict, total=False):
        key "disableLocalAuth": bool
        key "encryption": ForwardRef('EncryptionProperties', module='types')
        key "publicNetworkAccess": bool
        key "sku": ForwardRef('Sku', module='types')
        disable_local_auth: bool
        encryption: EncryptionProperties
        public_network_access: bool
        sku: Sku


    class azure.mgmt.automation.types.AutomationAccountUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('AutomationAccountUpdateProperties', module='types')
        identity: Identity
        location: str
        name: str
        properties: AutomationAccountUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.AutomationAccountUpdateProperties(TypedDict, total=False):
        key "disableLocalAuth": bool
        key "encryption": ForwardRef('EncryptionProperties', module='types')
        key "publicNetworkAccess": bool
        key "sku": ForwardRef('Sku', module='types')
        disable_local_auth: bool
        encryption: EncryptionProperties
        public_network_access: bool
        sku: Sku


    class azure.mgmt.automation.types.AutomationErrorResponse(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.automation.types.AzureQueryProperties(TypedDict, total=False):
        key "tagSettings": ForwardRef('TagSettingsProperties', module='types')
        locations: list[str]
        scope: list[str]
        tag_settings: TagSettingsProperties


    class azure.mgmt.automation.types.CertificateCreateOrUpdateParameters(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[CertificateCreateOrUpdateProperties]
        name: str
        properties: CertificateCreateOrUpdateProperties


    class azure.mgmt.automation.types.CertificateCreateOrUpdateProperties(TypedDict, total=False):
        key "base64Value": Required[str]
        key "description": str
        key "isExportable": bool
        key "thumbprint": str
        base64_value: str
        description: str
        is_exportable: bool
        thumbprint: str


    class azure.mgmt.automation.types.CertificateUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('CertificateUpdateProperties', module='types')
        name: str
        properties: CertificateUpdateProperties


    class azure.mgmt.automation.types.CertificateUpdateProperties(TypedDict, total=False):
        key "description": str
        description: str


    class azure.mgmt.automation.types.ConnectionCreateOrUpdateParameters(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[ConnectionCreateOrUpdateProperties]
        name: str
        properties: ConnectionCreateOrUpdateProperties


    class azure.mgmt.automation.types.ConnectionCreateOrUpdateProperties(TypedDict, total=False):
        key "connectionType": Required[ConnectionTypeAssociationProperty]
        key "description": str
        connection_type: ConnectionTypeAssociationProperty
        description: str
        fieldDefinitionValues: dict[str, str]
        field_definition_values: dict[str, str]


    class azure.mgmt.automation.types.ConnectionTypeAssociationProperty(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.automation.types.ConnectionTypeCreateOrUpdateParameters(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[ConnectionTypeCreateOrUpdateProperties]
        name: str
        properties: ConnectionTypeCreateOrUpdateProperties


    class azure.mgmt.automation.types.ConnectionTypeCreateOrUpdateProperties(TypedDict, total=False):
        key "fieldDefinitions": Required[dict[str, FieldDefinition]]
        key "isGlobal": bool
        field_definitions: dict[str, FieldDefinition]
        is_global: bool


    class azure.mgmt.automation.types.ConnectionUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ConnectionUpdateProperties', module='types')
        name: str
        properties: ConnectionUpdateProperties


    class azure.mgmt.automation.types.ConnectionUpdateProperties(TypedDict, total=False):
        key "description": str
        description: str
        fieldDefinitionValues: dict[str, str]
        field_definition_values: dict[str, str]


    class azure.mgmt.automation.types.ContentHash(TypedDict, total=False):
        key "algorithm": Required[str]
        key "value": Required[str]
        algorithm: str
        value: str


    class azure.mgmt.automation.types.ContentLink(TypedDict, total=False):
        key "contentHash": ForwardRef('ContentHash', module='types')
        key "uri": str
        key "version": str
        content_hash: ContentHash
        uri: str
        version: str


    class azure.mgmt.automation.types.ContentSource(TypedDict, total=False):
        key "hash": ForwardRef('ContentHash', module='types')
        key "type": Union[str, ContentSourceType]
        key "value": str
        key "version": str
        hash: ContentHash
        type: Union[str, ContentSourceType]
        value: str
        version: str


    class azure.mgmt.automation.types.CredentialCreateOrUpdateParameters(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[CredentialCreateOrUpdateProperties]
        name: str
        properties: CredentialCreateOrUpdateProperties


    class azure.mgmt.automation.types.CredentialCreateOrUpdateProperties(TypedDict, total=False):
        key "description": str
        key "password": Required[str]
        key "userName": Required[str]
        description: str
        password: str
        user_name: str


    class azure.mgmt.automation.types.CredentialUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('CredentialUpdateProperties', module='types')
        name: str
        properties: CredentialUpdateProperties


    class azure.mgmt.automation.types.CredentialUpdateProperties(TypedDict, total=False):
        key "description": str
        key "password": str
        key "userName": str
        description: str
        password: str
        user_name: str


    class azure.mgmt.automation.types.DscConfigurationAssociationProperty(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.automation.types.DscConfigurationCreateOrUpdateParameters(TypedDict, total=False):
        key "location": str
        key "name": str
        key "properties": Required[DscConfigurationCreateOrUpdateProperties]
        location: str
        name: str
        properties: DscConfigurationCreateOrUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.DscConfigurationCreateOrUpdateProperties(TypedDict, total=False):
        key "description": str
        key "logProgress": bool
        key "logVerbose": bool
        key "source": Required[ContentSource]
        description: str
        log_progress: bool
        log_verbose: bool
        parameters: dict[str, DscConfigurationParameter]
        source: ContentSource


    class azure.mgmt.automation.types.DscConfigurationParameter(TypedDict, total=False):
        key "defaultValue": str
        key "isMandatory": bool
        key "position": int
        key "type": str
        default_value: str
        is_mandatory: bool
        position: int
        type: str


    class azure.mgmt.automation.types.DscConfigurationUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('DscConfigurationCreateOrUpdateProperties', module='types')
        name: str
        properties: DscConfigurationCreateOrUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.DscNodeConfigurationAssociationProperty(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.automation.types.DscNodeConfigurationCreateOrUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('DscNodeConfigurationCreateOrUpdateParametersProperties', module='types')
        name: str
        properties: DscNodeConfigurationCreateOrUpdateParametersProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.DscNodeConfigurationCreateOrUpdateParametersProperties(TypedDict, total=False):
        key "configuration": Required[DscConfigurationAssociationProperty]
        key "incrementNodeConfigurationBuild": bool
        key "source": Required[ContentSource]
        configuration: DscConfigurationAssociationProperty
        increment_node_configuration_build: bool
        source: ContentSource


    class azure.mgmt.automation.types.DscNodeUpdateParameters(TypedDict, total=False):
        key "nodeId": str
        key "properties": ForwardRef('DscNodeUpdateParametersProperties', module='types')
        node_id: str
        properties: DscNodeUpdateParametersProperties


    class azure.mgmt.automation.types.DscNodeUpdateParametersProperties(TypedDict, total=False):
        key "nodeConfiguration": ForwardRef('DscNodeConfigurationAssociationProperty', module='types')
        node_configuration: DscNodeConfigurationAssociationProperty


    class azure.mgmt.automation.types.EncryptionProperties(TypedDict, total=False):
        key "identity": ForwardRef('EncryptionPropertiesIdentity', module='types')
        key "keySource": Union[str, EncryptionKeySourceType]
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        identity: EncryptionPropertiesIdentity
        key_source: Union[str, EncryptionKeySourceType]
        key_vault_properties: KeyVaultProperties


    class azure.mgmt.automation.types.EncryptionPropertiesIdentity(TypedDict, total=False):
        key "userAssignedIdentity": Any
        user_assigned_identity: Any


    class azure.mgmt.automation.types.FieldDefinition(TypedDict, total=False):
        key "isEncrypted": bool
        key "isOptional": bool
        key "type": Required[str]
        is_encrypted: bool
        is_optional: bool
        type: str


    class azure.mgmt.automation.types.GraphicalRunbookContent(TypedDict, total=False):
        key "graphRunbookJson": Optional[str]
        key "rawContent": Optional[RawGraphicalRunbookContent]
        graph_runbook_json: str
        raw_content: RawGraphicalRunbookContent


    class azure.mgmt.automation.types.HybridRunbookWorkerCreateOrUpdateParameters(TypedDict, total=False):
        key "vmResourceId": str
        vm_resource_id: str


    class azure.mgmt.automation.types.HybridRunbookWorkerCreateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('HybridRunbookWorkerCreateOrUpdateParameters', module='types')
        name: str
        properties: HybridRunbookWorkerCreateOrUpdateParameters


    class azure.mgmt.automation.types.HybridRunbookWorkerGroupCreateOrUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('HybridRunbookWorkerGroupCreateOrUpdateProperties', module='types')
        name: str
        properties: HybridRunbookWorkerGroupCreateOrUpdateProperties


    class azure.mgmt.automation.types.HybridRunbookWorkerGroupCreateOrUpdateProperties(TypedDict, total=False):
        key "credential": ForwardRef('RunAsCredentialAssociationProperty', module='types')
        credential: RunAsCredentialAssociationProperty


    class azure.mgmt.automation.types.HybridRunbookWorkerMoveParameters(TypedDict, total=False):
        key "hybridRunbookWorkerGroupName": str
        hybrid_runbook_worker_group_name: str


    class azure.mgmt.automation.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentitiesProperties]
        user_assigned_identities: dict[str, UserAssignedIdentitiesProperties]


    class azure.mgmt.automation.types.JobCreateParameters(TypedDict, total=False):
        key "properties": Required[JobCreateProperties]
        properties: JobCreateProperties


    class azure.mgmt.automation.types.JobCreateProperties(TypedDict, total=False):
        key "runOn": str
        key "runbook": ForwardRef('RunbookAssociationProperty', module='types')
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty


    class azure.mgmt.automation.types.JobScheduleCreateParameters(TypedDict, total=False):
        key "properties": Required[JobScheduleCreateProperties]
        properties: JobScheduleCreateProperties


    class azure.mgmt.automation.types.JobScheduleCreateProperties(TypedDict, total=False):
        key "runOn": str
        key "runbook": Required[RunbookAssociationProperty]
        key "schedule": Required[ScheduleAssociationProperty]
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty
        schedule: ScheduleAssociationProperty


    class azure.mgmt.automation.types.KeyVaultProperties(TypedDict, total=False):
        key "keyName": str
        key "keyVersion": str
        key "keyvaultUri": str
        key_name: str
        key_version: str
        keyvault_uri: str


    class azure.mgmt.automation.types.LinuxProperties(TypedDict, total=False):
        key "includedPackageClassifications": Union[str, LinuxUpdateClasses]
        key "rebootSetting": str
        excludedPackageNameMasks: list[str]
        excluded_package_name_masks: list[str]
        includedPackageNameMasks: list[str]
        included_package_classifications: Union[str, LinuxUpdateClasses]
        included_package_name_masks: list[str]
        reboot_setting: str


    class azure.mgmt.automation.types.ModuleCreateOrUpdateParameters(TypedDict, total=False):
        key "location": str
        key "name": str
        key "properties": Required[ModuleCreateOrUpdateProperties]
        location: str
        name: str
        properties: ModuleCreateOrUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.ModuleCreateOrUpdateProperties(TypedDict, total=False):
        key "contentLink": Required[ContentLink]
        content_link: ContentLink


    class azure.mgmt.automation.types.ModuleUpdateParameters(TypedDict, total=False):
        key "location": str
        key "name": str
        key "properties": ForwardRef('ModuleUpdateProperties', module='types')
        location: str
        name: str
        properties: ModuleUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.ModuleUpdateProperties(TypedDict, total=False):
        key "contentLink": ForwardRef('ContentLink', module='types')
        content_link: ContentLink


    class azure.mgmt.automation.types.NonAzureQueryProperties(TypedDict, total=False):
        key "functionAlias": str
        key "workspaceId": str
        function_alias: str
        workspace_id: str


    class azure.mgmt.automation.types.PackageCreateOrUpdateParameters(TypedDict, total=False):
        key "allOf": ForwardRef('TrackedResource', module='types')
        key "properties": Required[PackageCreateOrUpdateProperties]
        all_of: TrackedResource
        properties: PackageCreateOrUpdateProperties


    class azure.mgmt.automation.types.PackageCreateOrUpdateProperties(TypedDict, total=False):
        key "contentLink": Required[ContentLink]
        content_link: ContentLink


    class azure.mgmt.automation.types.PackageUpdateParameters(TypedDict, total=False):
        key "allOf": ForwardRef('TrackedResource', module='types')
        key "properties": ForwardRef('PackageUpdateProperties', module='types')
        all_of: TrackedResource
        properties: PackageUpdateProperties


    class azure.mgmt.automation.types.PackageUpdateProperties(TypedDict, total=False):
        key "contentLink": ForwardRef('ContentLink', module='types')
        content_link: ContentLink


    class azure.mgmt.automation.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.automation.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpointProperty', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionStateProperty', module='types')
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpointProperty
        private_link_service_connection_state: PrivateLinkServiceConnectionStateProperty


    class azure.mgmt.automation.types.PrivateEndpointProperty(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.automation.types.PrivateLinkServiceConnectionStateProperty(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": str
        actions_required: str
        description: str
        status: str


    class azure.mgmt.automation.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.automation.types.PythonPackageCreateParameters(TypedDict, total=False):
        key "properties": Required[PythonPackageCreateProperties]
        properties: PythonPackageCreateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.PythonPackageCreateProperties(TypedDict, total=False):
        key "contentLink": Required[ContentLink]
        content_link: ContentLink


    class azure.mgmt.automation.types.PythonPackageUpdateParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.automation.types.RawGraphicalRunbookContent(TypedDict, total=False):
        key "runbookDefinition": str
        key "runbookType": Union[str, GraphRunbookType]
        key "schemaVersion": str
        runbook_definition: str
        runbook_type: Union[str, GraphRunbookType]
        schema_version: str


    class azure.mgmt.automation.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.automation.types.RunAsCredentialAssociationProperty(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.automation.types.RunbookAssociationProperty(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.automation.types.RunbookCreateOrUpdateParameters(TypedDict, total=False):
        key "location": str
        key "name": str
        key "properties": Required[RunbookCreateOrUpdateProperties]
        location: str
        name: str
        properties: RunbookCreateOrUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.RunbookCreateOrUpdateProperties(TypedDict, total=False):
        key "description": str
        key "draft": ForwardRef('RunbookDraft', module='types')
        key "logActivityTrace": int
        key "logProgress": bool
        key "logVerbose": bool
        key "publishContentLink": ForwardRef('ContentLink', module='types')
        key "runbookType": Required[Union[str, RunbookTypeEnum]]
        key "runtimeEnvironment": str
        description: str
        draft: RunbookDraft
        log_activity_trace: int
        log_progress: bool
        log_verbose: bool
        publish_content_link: ContentLink
        runbook_type: Union[str, RunbookTypeEnum]
        runtime_environment: str


    class azure.mgmt.automation.types.RunbookDraft(TypedDict, total=False):
        key "creationTime": str
        key "draftContentLink": ForwardRef('ContentLink', module='types')
        key "inEdit": bool
        key "lastModifiedTime": str
        creation_time: str
        draft_content_link: ContentLink
        in_edit: bool
        last_modified_time: str
        outputTypes: list[str]
        output_types: list[str]
        parameters: dict[str, RunbookParameter]


    class azure.mgmt.automation.types.RunbookParameter(TypedDict, total=False):
        key "defaultValue": str
        key "isMandatory": bool
        key "position": int
        key "type": str
        default_value: str
        is_mandatory: bool
        position: int
        type: str


    class azure.mgmt.automation.types.RunbookUpdateParameters(TypedDict, total=False):
        key "location": str
        key "name": str
        key "properties": ForwardRef('RunbookUpdateProperties', module='types')
        location: str
        name: str
        properties: RunbookUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.automation.types.RunbookUpdateProperties(TypedDict, total=False):
        key "description": str
        key "logActivityTrace": int
        key "logProgress": bool
        key "logVerbose": bool
        description: str
        log_activity_trace: int
        log_progress: bool
        log_verbose: bool


    class azure.mgmt.automation.types.RuntimeEnvironment(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('RuntimeEnvironmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: RuntimeEnvironmentProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.automation.types.RuntimeEnvironmentProperties(TypedDict, total=False):
        key "description": str
        key "runtime": ForwardRef('RuntimeProperties', module='types')
        defaultPackages: dict[str, str]
        default_packages: dict[str, str]
        description: str
        runtime: RuntimeProperties


    class azure.mgmt.automation.types.RuntimeEnvironmentUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('RuntimeEnvironmentUpdateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        properties: RuntimeEnvironmentUpdateProperties
        system_data: SystemData


    class azure.mgmt.automation.types.RuntimeEnvironmentUpdateProperties(TypedDict, total=False):
        defaultPackages: dict[str, str]
        default_packages: dict[str, str]


    class azure.mgmt.automation.types.RuntimeProperties(TypedDict, total=False):
        key "language": str
        key "version": str
        language: str
        version: str


    class azure.mgmt.automation.types.SUCScheduleProperties(TypedDict, total=False):
        key "advancedSchedule": ForwardRef('AdvancedSchedule', module='types')
        key "creationTime": str
        key "description": str
        key "expiryTime": Optional[str]
        key "expiryTimeOffsetMinutes": float
        key "frequency": Union[str, ScheduleFrequency]
        key "interval": int
        key "isEnabled": bool
        key "lastModifiedTime": str
        key "nextRun": Optional[str]
        key "nextRunOffsetMinutes": float
        key "startTime": str
        key "startTimeOffsetMinutes": float
        key "timeZone": str
        advanced_schedule: AdvancedSchedule
        creation_time: str
        description: str
        expiry_time: str
        expiry_time_offset_minutes: float
        frequency: Union[str, ScheduleFrequency]
        interval: int
        is_enabled: bool
        last_modified_time: str
        next_run: str
        next_run_offset_minutes: float
        start_time: str
        start_time_offset_minutes: float
        time_zone: str


    class azure.mgmt.automation.types.ScheduleAssociationProperty(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.automation.types.ScheduleCreateOrUpdateParameters(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[ScheduleCreateOrUpdateProperties]
        name: str
        properties: ScheduleCreateOrUpdateProperties


    class azure.mgmt.automation.types.ScheduleCreateOrUpdateProperties(TypedDict, total=False):
        key "advancedSchedule": ForwardRef('AdvancedSchedule', module='types')
        key "description": str
        key "expiryTime": Optional[str]
        key "frequency": Required[Union[str, ScheduleFrequency]]
        key "interval": Any
        key "startTime": Required[str]
        key "timeZone": str
        advanced_schedule: AdvancedSchedule
        description: str
        expiry_time: str
        frequency: Union[str, ScheduleFrequency]
        interval: Any
        start_time: str
        time_zone: str


    class azure.mgmt.automation.types.ScheduleUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ScheduleUpdateProperties', module='types')
        name: str
        properties: ScheduleUpdateProperties


    class azure.mgmt.automation.types.ScheduleUpdateProperties(TypedDict, total=False):
        key "description": str
        key "isEnabled": bool
        description: str
        is_enabled: bool


    class azure.mgmt.automation.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[Union[str, SkuNameEnum]]
        capacity: int
        family: str
        name: Union[str, SkuNameEnum]


    class azure.mgmt.automation.types.SoftwareUpdateConfiguration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[SoftwareUpdateConfigurationProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SoftwareUpdateConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.automation.types.SoftwareUpdateConfigurationProperties(TypedDict, total=False):
        key "createdBy": str
        key "creationTime": str
        key "error": ForwardRef('AutomationErrorResponse', module='types')
        key "lastModifiedBy": str
        key "lastModifiedTime": str
        key "provisioningState": str
        key "scheduleInfo": Required[SUCScheduleProperties]
        key "tasks": ForwardRef('SoftwareUpdateConfigurationTasks', module='types')
        key "updateConfiguration": Required[UpdateConfiguration]
        created_by: str
        creation_time: str
        error: AutomationErrorResponse
        last_modified_by: str
        last_modified_time: str
        provisioning_state: str
        schedule_info: SUCScheduleProperties
        tasks: SoftwareUpdateConfigurationTasks
        update_configuration: UpdateConfiguration


    class azure.mgmt.automation.types.SoftwareUpdateConfigurationTasks(TypedDict, total=False):
        key "postTask": ForwardRef('TaskProperties', module='types')
        key "preTask": ForwardRef('TaskProperties', module='types')
        post_task: TaskProperties
        pre_task: TaskProperties


    class azure.mgmt.automation.types.SourceControlCreateOrUpdateParameters(TypedDict, total=False):
        key "properties": Required[SourceControlCreateOrUpdateProperties]
        properties: SourceControlCreateOrUpdateProperties


    class azure.mgmt.automation.types.SourceControlCreateOrUpdateProperties(TypedDict, total=False):
        key "autoSync": bool
        key "branch": str
        key "description": str
        key "folderPath": str
        key "publishRunbook": bool
        key "repoUrl": str
        key "securityToken": ForwardRef('SourceControlSecurityTokenProperties', module='types')
        key "sourceType": Union[str, SourceType]
        auto_sync: bool
        branch: str
        description: str
        folder_path: str
        publish_runbook: bool
        repo_url: str
        security_token: SourceControlSecurityTokenProperties
        source_type: Union[str, SourceType]


    class azure.mgmt.automation.types.SourceControlSecurityTokenProperties(TypedDict, total=False):
        key "accessToken": str
        key "refreshToken": str
        key "tokenType": Union[str, TokenType]
        access_token: str
        refresh_token: str
        token_type: Union[str, TokenType]


    class azure.mgmt.automation.types.SourceControlSyncJobCreateParameters(TypedDict, total=False):
        key "properties": Required[SourceControlSyncJobCreateProperties]
        properties: SourceControlSyncJobCreateProperties


    class azure.mgmt.automation.types.SourceControlSyncJobCreateProperties(TypedDict, total=False):
        key "commitId": Required[str]
        commit_id: str


    class azure.mgmt.automation.types.SourceControlUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('SourceControlUpdateProperties', module='types')
        properties: SourceControlUpdateProperties


    class azure.mgmt.automation.types.SourceControlUpdateProperties(TypedDict, total=False):
        key "autoSync": bool
        key "branch": str
        key "description": str
        key "folderPath": str
        key "publishRunbook": bool
        key "securityToken": ForwardRef('SourceControlSecurityTokenProperties', module='types')
        auto_sync: bool
        branch: str
        description: str
        folder_path: str
        publish_runbook: bool
        security_token: SourceControlSecurityTokenProperties


    class azure.mgmt.automation.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.automation.types.TagSettingsProperties(TypedDict, total=False):
        key "filterOperator": Union[str, TagOperators]
        filter_operator: Union[str, TagOperators]
        tags: dict[str, list[str]]


    class azure.mgmt.automation.types.TargetProperties(TypedDict, total=False):
        azureQueries: list[AzureQueryProperties]
        azure_queries: list[AzureQueryProperties]
        nonAzureQueries: list[NonAzureQueryProperties]
        non_azure_queries: list[NonAzureQueryProperties]


    class azure.mgmt.automation.types.TaskProperties(TypedDict, total=False):
        key "source": str
        parameters: dict[str, str]
        source: str


    class azure.mgmt.automation.types.TestJobCreateParameters(TypedDict, total=False):
        key "runOn": str
        key "runtimeEnvironment": str
        parameters: dict[str, str]
        run_on: str
        runtime_environment: str


    class azure.mgmt.automation.types.TrackedResource(Resource):
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


    class azure.mgmt.automation.types.UpdateConfiguration(TypedDict, total=False):
        key "duration": str
        key "linux": ForwardRef('LinuxProperties', module='types')
        key "operatingSystem": Required[Union[str, OperatingSystemType]]
        key "targets": ForwardRef('TargetProperties', module='types')
        key "windows": ForwardRef('WindowsProperties', module='types')
        azureVirtualMachines: list[str]
        azure_virtual_machines: list[str]
        duration: str
        linux: LinuxProperties
        nonAzureComputerNames: list[str]
        non_azure_computer_names: list[str]
        operating_system: Union[str, OperatingSystemType]
        targets: TargetProperties
        windows: WindowsProperties


    class azure.mgmt.automation.types.UserAssignedIdentitiesProperties(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.automation.types.VariableCreateOrUpdateParameters(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[VariableCreateOrUpdateProperties]
        name: str
        properties: VariableCreateOrUpdateProperties


    class azure.mgmt.automation.types.VariableCreateOrUpdateProperties(TypedDict, total=False):
        key "description": str
        key "isEncrypted": bool
        key "value": str
        description: str
        is_encrypted: bool
        value: str


    class azure.mgmt.automation.types.VariableUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('VariableUpdateProperties', module='types')
        name: str
        properties: VariableUpdateProperties


    class azure.mgmt.automation.types.VariableUpdateProperties(TypedDict, total=False):
        key "description": str
        key "value": str
        description: str
        value: str


    class azure.mgmt.automation.types.Watcher(ProxyResource):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('WatcherProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: WatcherProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.automation.types.WatcherProperties(TypedDict, total=False):
        key "creationTime": str
        key "description": str
        key "executionFrequencyInSeconds": int
        key "lastModifiedBy": str
        key "lastModifiedTime": str
        key "scriptName": str
        key "scriptRunOn": str
        key "status": str
        creation_time: str
        description: str
        execution_frequency_in_seconds: int
        last_modified_by: str
        last_modified_time: str
        scriptParameters: dict[str, str]
        script_name: str
        script_parameters: dict[str, str]
        script_run_on: str
        status: str


    class azure.mgmt.automation.types.WatcherUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('WatcherUpdateProperties', module='types')
        name: str
        properties: WatcherUpdateProperties


    class azure.mgmt.automation.types.WatcherUpdateProperties(TypedDict, total=False):
        key "executionFrequencyInSeconds": int
        execution_frequency_in_seconds: int


    class azure.mgmt.automation.types.WebhookCreateOrUpdateParameters(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[WebhookCreateOrUpdateProperties]
        name: str
        properties: WebhookCreateOrUpdateProperties


    class azure.mgmt.automation.types.WebhookCreateOrUpdateProperties(TypedDict, total=False):
        key "expiryTime": str
        key "isEnabled": bool
        key "runOn": str
        key "runbook": ForwardRef('RunbookAssociationProperty', module='types')
        key "uri": str
        expiry_time: str
        is_enabled: bool
        parameters: dict[str, str]
        run_on: str
        runbook: RunbookAssociationProperty
        uri: str


    class azure.mgmt.automation.types.WebhookUpdateParameters(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('WebhookUpdateProperties', module='types')
        name: str
        properties: WebhookUpdateProperties


    class azure.mgmt.automation.types.WebhookUpdateProperties(TypedDict, total=False):
        key "description": str
        key "isEnabled": bool
        key "runOn": str
        description: str
        is_enabled: bool
        parameters: dict[str, str]
        run_on: str


    class azure.mgmt.automation.types.WindowsProperties(TypedDict, total=False):
        key "includedUpdateClassifications": Union[str, WindowsUpdateClasses]
        key "rebootSetting": str
        excludedKbNumbers: list[str]
        excluded_kb_numbers: list[str]
        includedKbNumbers: list[str]
        included_kb_numbers: list[str]
        included_update_classifications: Union[str, WindowsUpdateClasses]
        reboot_setting: str


```