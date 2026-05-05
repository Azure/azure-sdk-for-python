```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.logic

    class azure.mgmt.logic.LogicManagementClient: implements ContextManager 
        integration_account_agreements: IntegrationAccountAgreementsOperations
        integration_account_assemblies: IntegrationAccountAssembliesOperations
        integration_account_batch_configurations: IntegrationAccountBatchConfigurationsOperations
        integration_account_certificates: IntegrationAccountCertificatesOperations
        integration_account_maps: IntegrationAccountMapsOperations
        integration_account_partners: IntegrationAccountPartnersOperations
        integration_account_schemas: IntegrationAccountSchemasOperations
        integration_account_sessions: IntegrationAccountSessionsOperations
        integration_accounts: IntegrationAccountsOperations
        integration_service_environment_managed_api_operations: IntegrationServiceEnvironmentManagedApiOperationsOperations
        integration_service_environment_managed_apis: IntegrationServiceEnvironmentManagedApisOperations
        integration_service_environment_network_health: IntegrationServiceEnvironmentNetworkHealthOperations
        integration_service_environment_skus: IntegrationServiceEnvironmentSkusOperations
        integration_service_environments: IntegrationServiceEnvironmentsOperations
        operations: Operations
        workflow_run_action_repetitions: WorkflowRunActionRepetitionsOperations
        workflow_run_action_repetitions_request_histories: WorkflowRunActionRepetitionsRequestHistoriesOperations
        workflow_run_action_request_histories: WorkflowRunActionRequestHistoriesOperations
        workflow_run_action_scope_repetitions: WorkflowRunActionScopeRepetitionsOperations
        workflow_run_actions: WorkflowRunActionsOperations
        workflow_run_operations: WorkflowRunOperationsOperations
        workflow_runs: WorkflowRunsOperations
        workflow_trigger_histories: WorkflowTriggerHistoriesOperations
        workflow_triggers: WorkflowTriggersOperations
        workflow_version_triggers: WorkflowVersionTriggersOperations
        workflow_versions: WorkflowVersionsOperations
        workflows: WorkflowsOperations

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


namespace azure.mgmt.logic.aio

    class azure.mgmt.logic.aio.LogicManagementClient: implements AsyncContextManager 
        integration_account_agreements: IntegrationAccountAgreementsOperations
        integration_account_assemblies: IntegrationAccountAssembliesOperations
        integration_account_batch_configurations: IntegrationAccountBatchConfigurationsOperations
        integration_account_certificates: IntegrationAccountCertificatesOperations
        integration_account_maps: IntegrationAccountMapsOperations
        integration_account_partners: IntegrationAccountPartnersOperations
        integration_account_schemas: IntegrationAccountSchemasOperations
        integration_account_sessions: IntegrationAccountSessionsOperations
        integration_accounts: IntegrationAccountsOperations
        integration_service_environment_managed_api_operations: IntegrationServiceEnvironmentManagedApiOperationsOperations
        integration_service_environment_managed_apis: IntegrationServiceEnvironmentManagedApisOperations
        integration_service_environment_network_health: IntegrationServiceEnvironmentNetworkHealthOperations
        integration_service_environment_skus: IntegrationServiceEnvironmentSkusOperations
        integration_service_environments: IntegrationServiceEnvironmentsOperations
        operations: Operations
        workflow_run_action_repetitions: WorkflowRunActionRepetitionsOperations
        workflow_run_action_repetitions_request_histories: WorkflowRunActionRepetitionsRequestHistoriesOperations
        workflow_run_action_request_histories: WorkflowRunActionRequestHistoriesOperations
        workflow_run_action_scope_repetitions: WorkflowRunActionScopeRepetitionsOperations
        workflow_run_actions: WorkflowRunActionsOperations
        workflow_run_operations: WorkflowRunOperationsOperations
        workflow_runs: WorkflowRunsOperations
        workflow_trigger_histories: WorkflowTriggerHistoriesOperations
        workflow_triggers: WorkflowTriggersOperations
        workflow_version_triggers: WorkflowVersionTriggersOperations
        workflow_versions: WorkflowVersionsOperations
        workflows: WorkflowsOperations

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


namespace azure.mgmt.logic.aio.operations

    class azure.mgmt.logic.aio.operations.IntegrationAccountAgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                agreement: IntegrationAccountAgreement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountAgreement: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                agreement: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountAgreement: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountAgreement: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccountAgreement]: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountAssembliesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                assembly_artifact: AssemblyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssemblyDefinition: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                assembly_artifact: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssemblyDefinition: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AssemblyDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AssemblyDefinition]: ...

        @distributed_trace_async
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountBatchConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                batch_configuration: BatchConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                batch_configuration: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BatchConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BatchConfiguration]: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                certificate: IntegrationAccountCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountCertificate: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                certificate: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountCertificate: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccountCertificate]: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountMapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                map: IntegrationAccountMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountMap: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                map: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountMap: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountMap: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccountMap]: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountPartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                partner: IntegrationAccountPartner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountPartner: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                partner: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountPartner: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountPartner: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccountPartner]: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                schema: IntegrationAccountSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSchema: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                schema: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSchema: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountSchema: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccountSchema]: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        async def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountSessionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                session: IntegrationAccountSession, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSession: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                session: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSession: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountSession: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccountSession]: ...


    class azure.mgmt.logic.aio.operations.IntegrationAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IntegrationAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccount]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationAccount]: ...

        @overload
        async def list_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                parameters: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CallbackUrl: ...

        @overload
        async def list_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CallbackUrl: ...

        @overload
        def list_key_vault_keys(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                list_key_vault_keys: ListKeyVaultKeysDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[KeyVaultKey]: ...

        @overload
        def list_key_vault_keys(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                list_key_vault_keys: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[KeyVaultKey]: ...

        @overload
        async def log_tracking_events(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                log_tracking_events: TrackingEventsDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def log_tracking_events(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                log_tracking_events: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def regenerate_access_key(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                regenerate_access_key: RegenerateActionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        async def regenerate_access_key(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                regenerate_access_key: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IntegrationAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...


    class azure.mgmt.logic.aio.operations.IntegrationServiceEnvironmentManagedApiOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ApiOperation]: ...


    class azure.mgmt.logic.aio.operations.IntegrationServiceEnvironmentManagedApisOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_put(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                integration_service_environment_managed_api: IntegrationServiceEnvironmentManagedApi, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationServiceEnvironmentManagedApi]: ...

        @overload
        async def begin_put(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                integration_service_environment_managed_api: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationServiceEnvironmentManagedApi]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationServiceEnvironmentManagedApi: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationServiceEnvironmentManagedApi]: ...


    class azure.mgmt.logic.aio.operations.IntegrationServiceEnvironmentNetworkHealthOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Dict[str, IntegrationServiceEnvironmentSubnetNetworkHealth]: ...


    class azure.mgmt.logic.aio.operations.IntegrationServiceEnvironmentSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationServiceEnvironmentSkuDefinition]: ...


    class azure.mgmt.logic.aio.operations.IntegrationServiceEnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IntegrationServiceEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationServiceEnvironment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationServiceEnvironment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IntegrationServiceEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationServiceEnvironment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IntegrationServiceEnvironment]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationServiceEnvironment: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationServiceEnvironment]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[IntegrationServiceEnvironment]: ...

        @distributed_trace_async
        async def restart(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.logic.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.logic.aio.operations.WorkflowRunActionRepetitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRunActionRepetitionDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkflowRunActionRepetitionDefinition]: ...

        @distributed_trace
        def list_expression_traces(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ExpressionRoot]: ...


    class azure.mgmt.logic.aio.operations.WorkflowRunActionRepetitionsRequestHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                request_history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RequestHistory: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RequestHistory]: ...


    class azure.mgmt.logic.aio.operations.WorkflowRunActionRequestHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                request_history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RequestHistory: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[RequestHistory]: ...


    class azure.mgmt.logic.aio.operations.WorkflowRunActionScopeRepetitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRunActionRepetitionDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkflowRunActionRepetitionDefinition]: ...


    class azure.mgmt.logic.aio.operations.WorkflowRunActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRunAction: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkflowRunAction]: ...

        @distributed_trace
        def list_expression_traces(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ExpressionRoot]: ...


    class azure.mgmt.logic.aio.operations.WorkflowRunOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRun: ...


    class azure.mgmt.logic.aio.operations.WorkflowRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkflowRun]: ...


    class azure.mgmt.logic.aio.operations.WorkflowTriggerHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTriggerHistory: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkflowTriggerHistory]: ...

        @distributed_trace_async
        async def resubmit(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.logic.aio.operations.WorkflowTriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTrigger: ...

        @distributed_trace_async
        async def get_schema_json(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JsonSchema: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkflowTrigger]: ...

        @distributed_trace_async
        async def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @distributed_trace_async
        async def reset(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def run(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_state(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                set_state: SetTriggerStateActionDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set_state(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                set_state: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.logic.aio.operations.WorkflowVersionTriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                version_id: str, 
                trigger_name: str, 
                parameters: Optional[GetCallbackUrlParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        async def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                version_id: str, 
                trigger_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.aio.operations.WorkflowVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                version_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[WorkflowVersion]: ...


    class azure.mgmt.logic.aio.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_move(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                move: WorkflowReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_move(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                move: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                workflow: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                workflow: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def generate_upgraded_definition(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: GenerateUpgradedDefinitionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def generate_upgraded_definition(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workflow]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Workflow]: ...

        @overload
        async def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                list_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        async def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                list_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @distributed_trace_async
        async def list_swagger(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def regenerate_access_key(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                key_type: RegenerateActionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def regenerate_access_key(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                key_type: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        async def validate_by_location(
                self, 
                resource_group_name: str, 
                location: str, 
                workflow_name: str, 
                validate: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate_by_location(
                self, 
                resource_group_name: str, 
                location: str, 
                workflow_name: str, 
                validate: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate_by_resource_group(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                validate: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate_by_resource_group(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                validate: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.logic.models

    class azure.mgmt.logic.models.AS2AcknowledgementConnectionSettings(Model):
        ignore_certificate_name_mismatch: bool
        keep_http_connection_alive: bool
        support_http_status_code_continue: bool
        unfold_http_headers: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                ignore_certificate_name_mismatch: bool, 
                keep_http_connection_alive: bool, 
                support_http_status_code_continue: bool, 
                unfold_http_headers: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2AgreementContent(Model):
        receive_agreement: AS2OneWayAgreement
        send_agreement: AS2OneWayAgreement

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                receive_agreement: AS2OneWayAgreement, 
                send_agreement: AS2OneWayAgreement, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2EnvelopeSettings(Model):
        autogenerate_file_name: bool
        file_name_template: str
        message_content_type: str
        suspend_message_on_file_name_generation_error: bool
        transmit_file_name_in_mime_header: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                autogenerate_file_name: bool, 
                file_name_template: str, 
                message_content_type: str, 
                suspend_message_on_file_name_generation_error: bool, 
                transmit_file_name_in_mime_header: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2ErrorSettings(Model):
        resend_if_mdn_not_received: bool
        suspend_duplicate_message: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resend_if_mdn_not_received: bool, 
                suspend_duplicate_message: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2MdnSettings(Model):
        disposition_notification_to: str
        mdn_text: str
        mic_hashing_algorithm: Union[str, HashingAlgorithm]
        need_mdn: bool
        receipt_delivery_url: str
        send_inbound_mdn_to_message_box: bool
        send_mdn_asynchronously: bool
        sign_mdn: bool
        sign_outbound_mdn_if_optional: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                disposition_notification_to: Optional[str] = ..., 
                mdn_text: Optional[str] = ..., 
                mic_hashing_algorithm: Union[str, HashingAlgorithm], 
                need_mdn: bool, 
                receipt_delivery_url: Optional[str] = ..., 
                send_inbound_mdn_to_message_box: bool, 
                send_mdn_asynchronously: bool, 
                sign_mdn: bool, 
                sign_outbound_mdn_if_optional: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2MessageConnectionSettings(Model):
        ignore_certificate_name_mismatch: bool
        keep_http_connection_alive: bool
        support_http_status_code_continue: bool
        unfold_http_headers: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                ignore_certificate_name_mismatch: bool, 
                keep_http_connection_alive: bool, 
                support_http_status_code_continue: bool, 
                unfold_http_headers: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2OneWayAgreement(Model):
        protocol_settings: AS2ProtocolSettings
        receiver_business_identity: BusinessIdentity
        sender_business_identity: BusinessIdentity

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                protocol_settings: AS2ProtocolSettings, 
                receiver_business_identity: BusinessIdentity, 
                sender_business_identity: BusinessIdentity, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2ProtocolSettings(Model):
        acknowledgement_connection_settings: AS2AcknowledgementConnectionSettings
        envelope_settings: AS2EnvelopeSettings
        error_settings: AS2ErrorSettings
        mdn_settings: AS2MdnSettings
        message_connection_settings: AS2MessageConnectionSettings
        security_settings: AS2SecuritySettings
        validation_settings: AS2ValidationSettings

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                acknowledgement_connection_settings: AS2AcknowledgementConnectionSettings, 
                envelope_settings: AS2EnvelopeSettings, 
                error_settings: AS2ErrorSettings, 
                mdn_settings: AS2MdnSettings, 
                message_connection_settings: AS2MessageConnectionSettings, 
                security_settings: AS2SecuritySettings, 
                validation_settings: AS2ValidationSettings, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2SecuritySettings(Model):
        enable_nrr_for_inbound_decoded_messages: bool
        enable_nrr_for_inbound_encoded_messages: bool
        enable_nrr_for_inbound_mdn: bool
        enable_nrr_for_outbound_decoded_messages: bool
        enable_nrr_for_outbound_encoded_messages: bool
        enable_nrr_for_outbound_mdn: bool
        encryption_certificate_name: str
        override_group_signing_certificate: bool
        sha2_algorithm_format: str
        signing_certificate_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                enable_nrr_for_inbound_decoded_messages: bool, 
                enable_nrr_for_inbound_encoded_messages: bool, 
                enable_nrr_for_inbound_mdn: bool, 
                enable_nrr_for_outbound_decoded_messages: bool, 
                enable_nrr_for_outbound_encoded_messages: bool, 
                enable_nrr_for_outbound_mdn: bool, 
                encryption_certificate_name: Optional[str] = ..., 
                override_group_signing_certificate: bool, 
                sha2_algorithm_format: Optional[str] = ..., 
                signing_certificate_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AS2ValidationSettings(Model):
        check_certificate_revocation_list_on_receive: bool
        check_certificate_revocation_list_on_send: bool
        check_duplicate_message: bool
        compress_message: bool
        encrypt_message: bool
        encryption_algorithm: Union[str, EncryptionAlgorithm]
        interchange_duplicates_validity_days: int
        override_message_properties: bool
        sign_message: bool
        signing_algorithm: Union[str, SigningAlgorithm]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                check_certificate_revocation_list_on_receive: bool, 
                check_certificate_revocation_list_on_send: bool, 
                check_duplicate_message: bool, 
                compress_message: bool, 
                encrypt_message: bool, 
                encryption_algorithm: Union[str, EncryptionAlgorithm], 
                interchange_duplicates_validity_days: int, 
                override_message_properties: bool, 
                sign_message: bool, 
                signing_algorithm: Optional[Union[str, SigningAlgorithm]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AgreementContent(Model):
        a_s2: AS2AgreementContent
        edifact: EdifactAgreementContent
        x12: X12AgreementContent

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                a_s2: Optional[AS2AgreementContent] = ..., 
                edifact: Optional[EdifactAgreementContent] = ..., 
                x12: Optional[X12AgreementContent] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AgreementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AS2 = "AS2"
        EDIFACT = "Edifact"
        NOT_SPECIFIED = "NotSpecified"
        X12 = "X12"


    class azure.mgmt.logic.models.ApiDeploymentParameterMetadata(Model):
        description: str
        display_name: str
        is_required: bool
        type: str
        visibility: Union[str, ApiDeploymentParameterVisibility]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                is_required: Optional[bool] = ..., 
                type: Optional[str] = ..., 
                visibility: Optional[Union[str, ApiDeploymentParameterVisibility]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiDeploymentParameterMetadataSet(Model):
        package_content_link: ApiDeploymentParameterMetadata
        redis_cache_connection_string: ApiDeploymentParameterMetadata

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                package_content_link: Optional[ApiDeploymentParameterMetadata] = ..., 
                redis_cache_connection_string: Optional[ApiDeploymentParameterMetadata] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiDeploymentParameterVisibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        INTERNAL = "Internal"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.ApiOperation(Resource):
        id: str
        location: str
        name: str
        properties: ApiOperationPropertiesDefinition
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ApiOperationPropertiesDefinition] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiOperationAnnotation(Model):
        family: str
        revision: int
        status: Union[str, StatusAnnotation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                family: Optional[str] = ..., 
                revision: Optional[int] = ..., 
                status: Optional[Union[str, StatusAnnotation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiOperationListResult(Model):
        next_link: str
        value: list[ApiOperation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ApiOperation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiOperationPropertiesDefinition(Model):
        annotation: ApiOperationAnnotation
        api: ApiReference
        description: str
        inputs_definition: SwaggerSchema
        is_notification: bool
        is_webhook: bool
        pageable: bool
        responses_definition: dict[str, SwaggerSchema]
        summary: str
        trigger: str
        trigger_hint: str
        visibility: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                annotation: Optional[ApiOperationAnnotation] = ..., 
                api: Optional[ApiReference] = ..., 
                description: Optional[str] = ..., 
                inputs_definition: Optional[SwaggerSchema] = ..., 
                is_notification: Optional[bool] = ..., 
                is_webhook: Optional[bool] = ..., 
                pageable: Optional[bool] = ..., 
                responses_definition: Optional[Dict[str, SwaggerSchema]] = ..., 
                summary: Optional[str] = ..., 
                trigger: Optional[str] = ..., 
                trigger_hint: Optional[str] = ..., 
                visibility: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiReference(ResourceReference):
        brand_color: str
        category: Union[str, ApiTier]
        description: str
        display_name: str
        icon_uri: str
        id: str
        integration_service_environment: ResourceReference
        name: str
        swagger: JSON
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                brand_color: Optional[str] = ..., 
                category: Optional[Union[str, ApiTier]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                icon_uri: Optional[str] = ..., 
                id: Optional[str] = ..., 
                integration_service_environment: Optional[ResourceReference] = ..., 
                swagger: Optional[JSON] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiResourceBackendService(Model):
        service_url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                service_url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiResourceDefinitions(Model):
        modified_swagger_url: str
        original_swagger_url: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                modified_swagger_url: Optional[str] = ..., 
                original_swagger_url: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiResourceGeneralInformation(Model):
        description: str
        display_name: str
        icon_url: str
        release_tag: str
        terms_of_use_url: str
        tier: Union[str, ApiTier]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                icon_url: Optional[str] = ..., 
                release_tag: Optional[str] = ..., 
                terms_of_use_url: Optional[str] = ..., 
                tier: Optional[Union[str, ApiTier]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiResourceMetadata(Model):
        api_type: Union[str, ApiType]
        brand_color: str
        connection_type: str
        deployment_parameters: ApiDeploymentParameterMetadataSet
        hide_key: str
        provisioning_state: Union[str, WorkflowProvisioningState]
        source: str
        tags: dict[str, str]
        wsdl_import_method: Union[str, WsdlImportMethod]
        wsdl_service: WsdlService

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                api_type: Optional[Union[str, ApiType]] = ..., 
                brand_color: Optional[str] = ..., 
                connection_type: Optional[str] = ..., 
                deployment_parameters: Optional[ApiDeploymentParameterMetadataSet] = ..., 
                hide_key: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, WorkflowProvisioningState]] = ..., 
                source: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                wsdl_import_method: Optional[Union[str, WsdlImportMethod]] = ..., 
                wsdl_service: Optional[WsdlService] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiResourcePolicies(Model):
        content: str
        content_link: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                content_link: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiResourceProperties(Model):
        api_definition_url: str
        api_definitions: ApiResourceDefinitions
        backend_service: ApiResourceBackendService
        capabilities: list[str]
        category: Union[str, ApiTier]
        connection_parameters: dict[str, JSON]
        general_information: ApiResourceGeneralInformation
        integration_service_environment: ResourceReference
        metadata: ApiResourceMetadata
        name: str
        policies: ApiResourcePolicies
        provisioning_state: Union[str, WorkflowProvisioningState]
        runtime_urls: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                integration_service_environment: Optional[ResourceReference] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ApiTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTERPRISE = "Enterprise"
        NOT_SPECIFIED = "NotSpecified"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.logic.models.ApiType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        REST = "Rest"
        SOAP = "Soap"


    class azure.mgmt.logic.models.ArtifactContentPropertiesDefinition(ArtifactProperties):
        changed_time: datetime
        content: any
        content_link: ContentLink
        content_type: str
        created_time: datetime
        metadata: any

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                changed_time: Optional[datetime] = ..., 
                content: Optional[Any] = ..., 
                content_link: Optional[ContentLink] = ..., 
                content_type: Optional[str] = ..., 
                created_time: Optional[datetime] = ..., 
                metadata: Optional[Any] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ArtifactProperties(Model):
        changed_time: datetime
        created_time: datetime
        metadata: any

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                changed_time: Optional[datetime] = ..., 
                created_time: Optional[datetime] = ..., 
                metadata: Optional[Any] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AssemblyCollection(Model):
        value: list[AssemblyDefinition]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AssemblyDefinition]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AssemblyDefinition(Resource):
        id: str
        location: str
        name: str
        properties: AssemblyProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: AssemblyProperties, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AssemblyProperties(ArtifactContentPropertiesDefinition):
        assembly_culture: str
        assembly_name: str
        assembly_public_key_token: str
        assembly_version: str
        changed_time: datetime
        content: any
        content_link: ContentLink
        content_type: str
        created_time: datetime
        metadata: any

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                assembly_culture: Optional[str] = ..., 
                assembly_name: str, 
                assembly_public_key_token: Optional[str] = ..., 
                assembly_version: Optional[str] = ..., 
                changed_time: Optional[datetime] = ..., 
                content: Optional[Any] = ..., 
                content_link: Optional[ContentLink] = ..., 
                content_type: Optional[str] = ..., 
                created_time: Optional[datetime] = ..., 
                metadata: Optional[Any] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.AzureAsyncOperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.logic.models.AzureResourceErrorInfo(ErrorInfo):
        code: str
        details: list[AzureResourceErrorInfo]
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[List[AzureResourceErrorInfo]] = ..., 
                message: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.B2BPartnerContent(Model):
        business_identities: list[BusinessIdentity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                business_identities: Optional[List[BusinessIdentity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.BatchConfiguration(Resource):
        id: str
        location: str
        name: str
        properties: BatchConfigurationProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: BatchConfigurationProperties, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.BatchConfigurationCollection(Model):
        value: list[BatchConfiguration]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[BatchConfiguration]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.BatchConfigurationProperties(ArtifactProperties):
        batch_group_name: str
        changed_time: datetime
        created_time: datetime
        metadata: any
        release_criteria: BatchReleaseCriteria

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                batch_group_name: str, 
                changed_time: Optional[datetime] = ..., 
                created_time: Optional[datetime] = ..., 
                metadata: Optional[Any] = ..., 
                release_criteria: BatchReleaseCriteria, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.BatchReleaseCriteria(Model):
        batch_size: int
        message_count: int
        recurrence: WorkflowTriggerRecurrence

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                batch_size: Optional[int] = ..., 
                message_count: Optional[int] = ..., 
                recurrence: Optional[WorkflowTriggerRecurrence] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.BusinessIdentity(Model):
        qualifier: str
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                qualifier: str, 
                value: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.CallbackUrl(Model):
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ContentHash(Model):
        algorithm: str
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                algorithm: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ContentLink(Model):
        content_hash: ContentHash
        content_size: int
        content_version: str
        metadata: JSON
        uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                uri: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.Correlation(Model):
        client_tracking_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                client_tracking_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.logic.models.DaysOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.logic.models.EdifactAcknowledgementSettings(Model):
        acknowledgement_control_number_lower_bound: int
        acknowledgement_control_number_prefix: str
        acknowledgement_control_number_suffix: str
        acknowledgement_control_number_upper_bound: int
        batch_functional_acknowledgements: bool
        batch_technical_acknowledgements: bool
        need_functional_acknowledgement: bool
        need_loop_for_valid_messages: bool
        need_technical_acknowledgement: bool
        rollover_acknowledgement_control_number: bool
        send_synchronous_acknowledgement: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                acknowledgement_control_number_lower_bound: int, 
                acknowledgement_control_number_prefix: Optional[str] = ..., 
                acknowledgement_control_number_suffix: Optional[str] = ..., 
                acknowledgement_control_number_upper_bound: int, 
                batch_functional_acknowledgements: bool, 
                batch_technical_acknowledgements: bool, 
                need_functional_acknowledgement: bool, 
                need_loop_for_valid_messages: bool, 
                need_technical_acknowledgement: bool, 
                rollover_acknowledgement_control_number: bool, 
                send_synchronous_acknowledgement: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactAgreementContent(Model):
        receive_agreement: EdifactOneWayAgreement
        send_agreement: EdifactOneWayAgreement

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                receive_agreement: EdifactOneWayAgreement, 
                send_agreement: EdifactOneWayAgreement, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactCharacterSet(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KECA = "KECA"
        NOT_SPECIFIED = "NotSpecified"
        UNOA = "UNOA"
        UNOB = "UNOB"
        UNOC = "UNOC"
        UNOD = "UNOD"
        UNOE = "UNOE"
        UNOF = "UNOF"
        UNOG = "UNOG"
        UNOH = "UNOH"
        UNOI = "UNOI"
        UNOJ = "UNOJ"
        UNOK = "UNOK"
        UNOX = "UNOX"
        UNOY = "UNOY"


    class azure.mgmt.logic.models.EdifactDecimalIndicator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMA = "Comma"
        DECIMAL = "Decimal"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.EdifactDelimiterOverride(Model):
        component_separator: int
        data_element_separator: int
        decimal_point_indicator: Union[str, EdifactDecimalIndicator]
        message_association_assigned_code: str
        message_id: str
        message_release: str
        message_version: str
        release_indicator: int
        repetition_separator: int
        segment_terminator: int
        segment_terminator_suffix: Union[str, SegmentTerminatorSuffix]
        target_namespace: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                component_separator: int, 
                data_element_separator: int, 
                decimal_point_indicator: Union[str, EdifactDecimalIndicator], 
                message_association_assigned_code: Optional[str] = ..., 
                message_id: Optional[str] = ..., 
                message_release: Optional[str] = ..., 
                message_version: Optional[str] = ..., 
                release_indicator: int, 
                repetition_separator: int, 
                segment_terminator: int, 
                segment_terminator_suffix: Union[str, SegmentTerminatorSuffix], 
                target_namespace: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactEnvelopeOverride(Model):
        application_password: str
        association_assigned_code: str
        controlling_agency_code: str
        functional_group_id: str
        group_header_message_release: str
        group_header_message_version: str
        message_association_assigned_code: str
        message_id: str
        message_release: str
        message_version: str
        receiver_application_id: str
        receiver_application_qualifier: str
        sender_application_id: str
        sender_application_qualifier: str
        target_namespace: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                application_password: Optional[str] = ..., 
                association_assigned_code: Optional[str] = ..., 
                controlling_agency_code: Optional[str] = ..., 
                functional_group_id: Optional[str] = ..., 
                group_header_message_release: Optional[str] = ..., 
                group_header_message_version: Optional[str] = ..., 
                message_association_assigned_code: Optional[str] = ..., 
                message_id: Optional[str] = ..., 
                message_release: Optional[str] = ..., 
                message_version: Optional[str] = ..., 
                receiver_application_id: Optional[str] = ..., 
                receiver_application_qualifier: Optional[str] = ..., 
                sender_application_id: Optional[str] = ..., 
                sender_application_qualifier: Optional[str] = ..., 
                target_namespace: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactEnvelopeSettings(Model):
        application_reference_id: str
        apply_delimiter_string_advice: bool
        communication_agreement_id: str
        create_grouping_segments: bool
        enable_default_group_headers: bool
        functional_group_id: str
        group_application_password: str
        group_application_receiver_id: str
        group_application_receiver_qualifier: str
        group_application_sender_id: str
        group_application_sender_qualifier: str
        group_association_assigned_code: str
        group_control_number_lower_bound: int
        group_control_number_prefix: str
        group_control_number_suffix: str
        group_control_number_upper_bound: int
        group_controlling_agency_code: str
        group_message_release: str
        group_message_version: str
        interchange_control_number_lower_bound: int
        interchange_control_number_prefix: str
        interchange_control_number_suffix: str
        interchange_control_number_upper_bound: int
        is_test_interchange: bool
        overwrite_existing_transaction_set_control_number: bool
        processing_priority_code: str
        receiver_internal_identification: str
        receiver_internal_sub_identification: str
        receiver_reverse_routing_address: str
        recipient_reference_password_qualifier: str
        recipient_reference_password_value: str
        rollover_group_control_number: bool
        rollover_interchange_control_number: bool
        rollover_transaction_set_control_number: bool
        sender_internal_identification: str
        sender_internal_sub_identification: str
        sender_reverse_routing_address: str
        transaction_set_control_number_lower_bound: int
        transaction_set_control_number_prefix: str
        transaction_set_control_number_suffix: str
        transaction_set_control_number_upper_bound: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                application_reference_id: Optional[str] = ..., 
                apply_delimiter_string_advice: bool, 
                communication_agreement_id: Optional[str] = ..., 
                create_grouping_segments: bool, 
                enable_default_group_headers: bool, 
                functional_group_id: Optional[str] = ..., 
                group_application_password: Optional[str] = ..., 
                group_application_receiver_id: Optional[str] = ..., 
                group_application_receiver_qualifier: Optional[str] = ..., 
                group_application_sender_id: Optional[str] = ..., 
                group_application_sender_qualifier: Optional[str] = ..., 
                group_association_assigned_code: Optional[str] = ..., 
                group_control_number_lower_bound: int, 
                group_control_number_prefix: Optional[str] = ..., 
                group_control_number_suffix: Optional[str] = ..., 
                group_control_number_upper_bound: int, 
                group_controlling_agency_code: Optional[str] = ..., 
                group_message_release: Optional[str] = ..., 
                group_message_version: Optional[str] = ..., 
                interchange_control_number_lower_bound: int, 
                interchange_control_number_prefix: Optional[str] = ..., 
                interchange_control_number_suffix: Optional[str] = ..., 
                interchange_control_number_upper_bound: int, 
                is_test_interchange: bool, 
                overwrite_existing_transaction_set_control_number: bool, 
                processing_priority_code: Optional[str] = ..., 
                receiver_internal_identification: Optional[str] = ..., 
                receiver_internal_sub_identification: Optional[str] = ..., 
                receiver_reverse_routing_address: Optional[str] = ..., 
                recipient_reference_password_qualifier: Optional[str] = ..., 
                recipient_reference_password_value: Optional[str] = ..., 
                rollover_group_control_number: bool, 
                rollover_interchange_control_number: bool, 
                rollover_transaction_set_control_number: bool, 
                sender_internal_identification: Optional[str] = ..., 
                sender_internal_sub_identification: Optional[str] = ..., 
                sender_reverse_routing_address: Optional[str] = ..., 
                transaction_set_control_number_lower_bound: int, 
                transaction_set_control_number_prefix: Optional[str] = ..., 
                transaction_set_control_number_suffix: Optional[str] = ..., 
                transaction_set_control_number_upper_bound: int, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactFramingSettings(Model):
        character_encoding: str
        character_set: Union[str, EdifactCharacterSet]
        component_separator: int
        data_element_separator: int
        decimal_point_indicator: Union[str, EdifactDecimalIndicator]
        protocol_version: int
        release_indicator: int
        repetition_separator: int
        segment_terminator: int
        segment_terminator_suffix: Union[str, SegmentTerminatorSuffix]
        service_code_list_directory_version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                character_encoding: Optional[str] = ..., 
                character_set: Union[str, EdifactCharacterSet], 
                component_separator: int, 
                data_element_separator: int, 
                decimal_point_indicator: Union[str, EdifactDecimalIndicator], 
                protocol_version: int, 
                release_indicator: int, 
                repetition_separator: int, 
                segment_terminator: int, 
                segment_terminator_suffix: Union[str, SegmentTerminatorSuffix], 
                service_code_list_directory_version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactMessageFilter(Model):
        message_filter_type: Union[str, MessageFilterType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                message_filter_type: Union[str, MessageFilterType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactMessageIdentifier(Model):
        message_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                message_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactOneWayAgreement(Model):
        protocol_settings: EdifactProtocolSettings
        receiver_business_identity: BusinessIdentity
        sender_business_identity: BusinessIdentity

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                protocol_settings: EdifactProtocolSettings, 
                receiver_business_identity: BusinessIdentity, 
                sender_business_identity: BusinessIdentity, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactProcessingSettings(Model):
        create_empty_xml_tags_for_trailing_separators: bool
        mask_security_info: bool
        preserve_interchange: bool
        suspend_interchange_on_error: bool
        use_dot_as_decimal_separator: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                create_empty_xml_tags_for_trailing_separators: bool, 
                mask_security_info: bool, 
                preserve_interchange: bool, 
                suspend_interchange_on_error: bool, 
                use_dot_as_decimal_separator: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactProtocolSettings(Model):
        acknowledgement_settings: EdifactAcknowledgementSettings
        edifact_delimiter_overrides: list[EdifactDelimiterOverride]
        envelope_overrides: list[EdifactEnvelopeOverride]
        envelope_settings: EdifactEnvelopeSettings
        framing_settings: EdifactFramingSettings
        message_filter: EdifactMessageFilter
        message_filter_list: list[EdifactMessageIdentifier]
        processing_settings: EdifactProcessingSettings
        schema_references: list[EdifactSchemaReference]
        validation_overrides: list[EdifactValidationOverride]
        validation_settings: EdifactValidationSettings

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                acknowledgement_settings: EdifactAcknowledgementSettings, 
                edifact_delimiter_overrides: Optional[List[EdifactDelimiterOverride]] = ..., 
                envelope_overrides: Optional[List[EdifactEnvelopeOverride]] = ..., 
                envelope_settings: EdifactEnvelopeSettings, 
                framing_settings: EdifactFramingSettings, 
                message_filter: EdifactMessageFilter, 
                message_filter_list: Optional[List[EdifactMessageIdentifier]] = ..., 
                processing_settings: EdifactProcessingSettings, 
                schema_references: List[EdifactSchemaReference], 
                validation_overrides: Optional[List[EdifactValidationOverride]] = ..., 
                validation_settings: EdifactValidationSettings, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactSchemaReference(Model):
        association_assigned_code: str
        message_id: str
        message_release: str
        message_version: str
        schema_name: str
        sender_application_id: str
        sender_application_qualifier: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                association_assigned_code: Optional[str] = ..., 
                message_id: str, 
                message_release: str, 
                message_version: str, 
                schema_name: str, 
                sender_application_id: Optional[str] = ..., 
                sender_application_qualifier: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactValidationOverride(Model):
        allow_leading_and_trailing_spaces_and_zeroes: bool
        enforce_character_set: bool
        message_id: str
        trailing_separator_policy: Union[str, TrailingSeparatorPolicy]
        trim_leading_and_trailing_spaces_and_zeroes: bool
        validate_edi_types: bool
        validate_xsd_types: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allow_leading_and_trailing_spaces_and_zeroes: bool, 
                enforce_character_set: bool, 
                message_id: str, 
                trailing_separator_policy: Union[str, TrailingSeparatorPolicy], 
                trim_leading_and_trailing_spaces_and_zeroes: bool, 
                validate_edi_types: bool, 
                validate_xsd_types: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EdifactValidationSettings(Model):
        allow_leading_and_trailing_spaces_and_zeroes: bool
        check_duplicate_group_control_number: bool
        check_duplicate_interchange_control_number: bool
        check_duplicate_transaction_set_control_number: bool
        interchange_control_number_validity_days: int
        trailing_separator_policy: Union[str, TrailingSeparatorPolicy]
        trim_leading_and_trailing_spaces_and_zeroes: bool
        validate_character_set: bool
        validate_edi_types: bool
        validate_xsd_types: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allow_leading_and_trailing_spaces_and_zeroes: bool, 
                check_duplicate_group_control_number: bool, 
                check_duplicate_interchange_control_number: bool, 
                check_duplicate_transaction_set_control_number: bool, 
                interchange_control_number_validity_days: int, 
                trailing_separator_policy: Union[str, TrailingSeparatorPolicy], 
                trim_leading_and_trailing_spaces_and_zeroes: bool, 
                validate_character_set: bool, 
                validate_edi_types: bool, 
                validate_xsd_types: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.EncryptionAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AES128 = "AES128"
        AES192 = "AES192"
        AES256 = "AES256"
        DES3 = "DES3"
        NONE = "None"
        NOT_SPECIFIED = "NotSpecified"
        RC2 = "RC2"


    class azure.mgmt.logic.models.ErrorInfo(Model):
        code: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ErrorProperties(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ErrorResponse(Model):
        error: ErrorProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ErrorResponseCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTEGRATION_SERVICE_ENVIRONMENT_NOT_FOUND = "IntegrationServiceEnvironmentNotFound"
        INTERNAL_SERVER_ERROR = "InternalServerError"
        INVALID_OPERATION_ID = "InvalidOperationId"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.EventLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        ERROR = "Error"
        INFORMATIONAL = "Informational"
        LOG_ALWAYS = "LogAlways"
        VERBOSE = "Verbose"
        WARNING = "Warning"


    class azure.mgmt.logic.models.Expression(Model):
        error: AzureResourceErrorInfo
        subexpressions: list[Expression]
        text: str
        value: any

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[AzureResourceErrorInfo] = ..., 
                subexpressions: Optional[List[Expression]] = ..., 
                text: Optional[str] = ..., 
                value: Optional[Any] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ExpressionRoot(Expression):
        error: AzureResourceErrorInfo
        path: str
        subexpressions: list[Expression]
        text: str
        value: any

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[AzureResourceErrorInfo] = ..., 
                path: Optional[str] = ..., 
                subexpressions: Optional[List[Expression]] = ..., 
                text: Optional[str] = ..., 
                value: Optional[Any] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ExpressionTraces(Model):
        inputs: list[ExpressionRoot]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                inputs: Optional[List[ExpressionRoot]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ExtendedErrorInfo(Model):
        code: Union[str, ErrorResponseCode]
        details: list[ExtendedErrorInfo]
        inner_error: JSON
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Union[str, ErrorResponseCode], 
                details: Optional[List[ExtendedErrorInfo]] = ..., 
                inner_error: Optional[JSON] = ..., 
                message: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.FlowAccessControlConfiguration(Model):
        actions: FlowAccessControlConfigurationPolicy
        contents: FlowAccessControlConfigurationPolicy
        triggers: FlowAccessControlConfigurationPolicy
        workflow_management: FlowAccessControlConfigurationPolicy

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                actions: Optional[FlowAccessControlConfigurationPolicy] = ..., 
                contents: Optional[FlowAccessControlConfigurationPolicy] = ..., 
                triggers: Optional[FlowAccessControlConfigurationPolicy] = ..., 
                workflow_management: Optional[FlowAccessControlConfigurationPolicy] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.FlowAccessControlConfigurationPolicy(Model):
        allowed_caller_ip_addresses: list[IpAddressRange]
        open_authentication_policies: OpenAuthenticationAccessPolicies

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allowed_caller_ip_addresses: Optional[List[IpAddressRange]] = ..., 
                open_authentication_policies: Optional[OpenAuthenticationAccessPolicies] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.FlowEndpoints(Model):
        access_endpoint_ip_addresses: list[IpAddress]
        outgoing_ip_addresses: list[IpAddress]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_endpoint_ip_addresses: Optional[List[IpAddress]] = ..., 
                outgoing_ip_addresses: Optional[List[IpAddress]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.FlowEndpointsConfiguration(Model):
        connector: FlowEndpoints
        workflow: FlowEndpoints

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                connector: Optional[FlowEndpoints] = ..., 
                workflow: Optional[FlowEndpoints] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.GenerateUpgradedDefinitionParameters(Model):
        target_schema_version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                target_schema_version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.GetCallbackUrlParameters(Model):
        key_type: Union[str, KeyType]
        not_after: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key_type: Optional[Union[str, KeyType]] = ..., 
                not_after: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.HashingAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MD5 = "MD5"
        NONE = "None"
        NOT_SPECIFIED = "NotSpecified"
        SHA1 = "SHA1"
        SHA2256 = "SHA2256"
        SHA2384 = "SHA2384"
        SHA2512 = "SHA2512"


    class azure.mgmt.logic.models.IntegrationAccount(Resource):
        id: str
        integration_service_environment: ResourceReference
        location: str
        name: str
        sku: IntegrationAccountSku
        state: Union[str, WorkflowState]
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                integration_service_environment: Optional[ResourceReference] = ..., 
                location: Optional[str] = ..., 
                sku: Optional[IntegrationAccountSku] = ..., 
                state: Optional[Union[str, WorkflowState]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountAgreement(Resource):
        agreement_type: Union[str, AgreementType]
        changed_time: datetime
        content: AgreementContent
        created_time: datetime
        guest_identity: BusinessIdentity
        guest_partner: str
        host_identity: BusinessIdentity
        host_partner: str
        id: str
        location: str
        metadata: JSON
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                agreement_type: Union[str, AgreementType], 
                content: AgreementContent, 
                guest_identity: BusinessIdentity, 
                guest_partner: str, 
                host_identity: BusinessIdentity, 
                host_partner: str, 
                location: Optional[str] = ..., 
                metadata: Optional[JSON] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountAgreementFilter(Model):
        agreement_type: Union[str, AgreementType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                agreement_type: Union[str, AgreementType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountAgreementListResult(Model):
        next_link: str
        value: list[IntegrationAccountAgreement]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationAccountAgreement]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountCertificate(Resource):
        changed_time: datetime
        created_time: datetime
        id: str
        key: KeyVaultKeyReference
        location: str
        metadata: JSON
        name: str
        public_certificate: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key: Optional[KeyVaultKeyReference] = ..., 
                location: Optional[str] = ..., 
                metadata: Optional[JSON] = ..., 
                public_certificate: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountCertificateListResult(Model):
        next_link: str
        value: list[IntegrationAccountCertificate]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationAccountCertificate]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountListResult(Model):
        next_link: str
        value: list[IntegrationAccount]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationAccount]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountMap(Resource):
        changed_time: datetime
        content: str
        content_link: ContentLink
        content_type: str
        created_time: datetime
        id: str
        location: str
        map_type: Union[str, MapType]
        metadata: JSON
        name: str
        parameters_schema: IntegrationAccountMapPropertiesParametersSchema
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                content_type: Optional[str] = ..., 
                location: Optional[str] = ..., 
                map_type: Union[str, MapType], 
                metadata: Optional[JSON] = ..., 
                parameters_schema: Optional[IntegrationAccountMapPropertiesParametersSchema] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountMapFilter(Model):
        map_type: Union[str, MapType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                map_type: Union[str, MapType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountMapListResult(Model):
        next_link: str
        value: list[IntegrationAccountMap]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationAccountMap]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountMapPropertiesParametersSchema(Model):
        ref: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                ref: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountPartner(Resource):
        changed_time: datetime
        content: PartnerContent
        created_time: datetime
        id: str
        location: str
        metadata: JSON
        name: str
        partner_type: Union[str, PartnerType]
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: PartnerContent, 
                location: Optional[str] = ..., 
                metadata: Optional[JSON] = ..., 
                partner_type: Union[str, PartnerType], 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountPartnerFilter(Model):
        partner_type: Union[str, PartnerType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                partner_type: Union[str, PartnerType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountPartnerListResult(Model):
        next_link: str
        value: list[IntegrationAccountPartner]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationAccountPartner]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSchema(Resource):
        changed_time: datetime
        content: str
        content_link: ContentLink
        content_type: str
        created_time: datetime
        document_name: str
        file_name: str
        id: str
        location: str
        metadata: JSON
        name: str
        schema_type: Union[str, SchemaType]
        tags: dict[str, str]
        target_namespace: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                content_type: Optional[str] = ..., 
                document_name: Optional[str] = ..., 
                file_name: Optional[str] = ..., 
                location: Optional[str] = ..., 
                metadata: Optional[JSON] = ..., 
                schema_type: Union[str, SchemaType], 
                tags: Optional[Dict[str, str]] = ..., 
                target_namespace: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSchemaFilter(Model):
        schema_type: Union[str, SchemaType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                schema_type: Union[str, SchemaType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSchemaListResult(Model):
        next_link: str
        value: list[IntegrationAccountSchema]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationAccountSchema]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSession(Resource):
        changed_time: datetime
        content: JSON
        created_time: datetime
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[JSON] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSessionFilter(Model):
        changed_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                changed_time: datetime, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSessionListResult(Model):
        next_link: str
        value: list[IntegrationAccountSession]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationAccountSession]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSku(Model):
        name: Union[str, IntegrationAccountSkuName]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Union[str, IntegrationAccountSkuName], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationAccountSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        NOT_SPECIFIED = "NotSpecified"
        STANDARD = "Standard"


    class azure.mgmt.logic.models.IntegrationServiceEnvironmenEncryptionConfiguration(Model):
        encryption_key_reference: IntegrationServiceEnvironmenEncryptionKeyReference

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                encryption_key_reference: Optional[IntegrationServiceEnvironmenEncryptionKeyReference] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmenEncryptionKeyReference(Model):
        key_name: str
        key_vault: ResourceReference
        key_version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_vault: Optional[ResourceReference] = ..., 
                key_version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironment(Resource):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: IntegrationServiceEnvironmentProperties
        sku: IntegrationServiceEnvironmentSku
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[IntegrationServiceEnvironmentProperties] = ..., 
                sku: Optional[IntegrationServiceEnvironmentSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentAccessEndpoint(Model):
        type: Union[str, IntegrationServiceEnvironmentAccessEndpointType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IntegrationServiceEnvironmentAccessEndpointType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentAccessEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        INTERNAL = "Internal"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentListResult(Model):
        next_link: str
        value: list[IntegrationServiceEnvironment]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationServiceEnvironment]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentManagedApi(Resource):
        api_definition_url: str
        api_definitions: ApiResourceDefinitions
        backend_service: ApiResourceBackendService
        capabilities: list[str]
        category: Union[str, ApiTier]
        connection_parameters: dict[str, JSON]
        deployment_parameters: IntegrationServiceEnvironmentManagedApiDeploymentParameters
        general_information: ApiResourceGeneralInformation
        id: str
        integration_service_environment: ResourceReference
        location: str
        metadata: ApiResourceMetadata
        name: str
        name_properties_name: str
        policies: ApiResourcePolicies
        provisioning_state: Union[str, WorkflowProvisioningState]
        runtime_urls: list[str]
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                deployment_parameters: Optional[IntegrationServiceEnvironmentManagedApiDeploymentParameters] = ..., 
                integration_service_environment: Optional[ResourceReference] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentManagedApiDeploymentParameters(Model):
        content_link_definition: ContentLink

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content_link_definition: Optional[ContentLink] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentManagedApiListResult(Model):
        next_link: str
        value: list[IntegrationServiceEnvironmentManagedApi]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationServiceEnvironmentManagedApi]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentManagedApiProperties(ApiResourceProperties):
        api_definition_url: str
        api_definitions: ApiResourceDefinitions
        backend_service: ApiResourceBackendService
        capabilities: list[str]
        category: Union[str, ApiTier]
        connection_parameters: dict[str, JSON]
        deployment_parameters: IntegrationServiceEnvironmentManagedApiDeploymentParameters
        general_information: ApiResourceGeneralInformation
        integration_service_environment: ResourceReference
        metadata: ApiResourceMetadata
        name: str
        policies: ApiResourcePolicies
        provisioning_state: Union[str, WorkflowProvisioningState]
        runtime_urls: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                deployment_parameters: Optional[IntegrationServiceEnvironmentManagedApiDeploymentParameters] = ..., 
                integration_service_environment: Optional[ResourceReference] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentNetworkDependency(Model):
        category: Union[str, IntegrationServiceEnvironmentNetworkDependencyCategoryType]
        display_name: str
        endpoints: list[IntegrationServiceEnvironmentNetworkEndpoint]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                category: Optional[Union[str, IntegrationServiceEnvironmentNetworkDependencyCategoryType]] = ..., 
                display_name: Optional[str] = ..., 
                endpoints: Optional[List[IntegrationServiceEnvironmentNetworkEndpoint]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentNetworkDependencyCategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_ENDPOINTS = "AccessEndpoints"
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        AZURE_MANAGEMENT = "AzureManagement"
        AZURE_STORAGE = "AzureStorage"
        DIAGNOSTIC_LOGS_AND_METRICS = "DiagnosticLogsAndMetrics"
        INTEGRATION_SERVICE_ENVIRONMENT_CONNECTORS = "IntegrationServiceEnvironmentConnectors"
        NOT_SPECIFIED = "NotSpecified"
        RECOVERY_SERVICE = "RecoveryService"
        REDIS_CACHE = "RedisCache"
        REGIONAL_SERVICE = "RegionalService"
        SQL = "SQL"
        SSL_CERTIFICATE_VERIFICATION = "SSLCertificateVerification"


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentNetworkDependencyHealth(Model):
        error: ExtendedErrorInfo
        state: Union[str, IntegrationServiceEnvironmentNetworkDependencyHealthState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ExtendedErrorInfo] = ..., 
                state: Optional[Union[str, IntegrationServiceEnvironmentNetworkDependencyHealthState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentNetworkDependencyHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        NOT_SPECIFIED = "NotSpecified"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentNetworkEndPointAccessibilityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        NOT_AVAILABLE = "NotAvailable"
        NOT_SPECIFIED = "NotSpecified"
        UNKNOWN = "Unknown"


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentNetworkEndpoint(Model):
        accessibility: Union[str, IntegrationServiceEnvironmentNetworkEndPointAccessibilityState]
        domain_name: str
        ports: list[str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                accessibility: Optional[Union[str, IntegrationServiceEnvironmentNetworkEndPointAccessibilityState]] = ..., 
                domain_name: Optional[str] = ..., 
                ports: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentProperties(Model):
        encryption_configuration: IntegrationServiceEnvironmenEncryptionConfiguration
        endpoints_configuration: FlowEndpointsConfiguration
        integration_service_environment_id: str
        network_configuration: NetworkConfiguration
        provisioning_state: Union[str, WorkflowProvisioningState]
        state: Union[str, WorkflowState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                encryption_configuration: Optional[IntegrationServiceEnvironmenEncryptionConfiguration] = ..., 
                endpoints_configuration: Optional[FlowEndpointsConfiguration] = ..., 
                integration_service_environment_id: Optional[str] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                provisioning_state: Optional[Union[str, WorkflowProvisioningState]] = ..., 
                state: Optional[Union[str, WorkflowState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSku(Model):
        capacity: int
        name: Union[str, IntegrationServiceEnvironmentSkuName]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, IntegrationServiceEnvironmentSkuName]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSkuCapacity(Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, IntegrationServiceEnvironmentSkuScaleType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                default: Optional[int] = ..., 
                maximum: Optional[int] = ..., 
                minimum: Optional[int] = ..., 
                scale_type: Optional[Union[str, IntegrationServiceEnvironmentSkuScaleType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSkuDefinition(Model):
        capacity: IntegrationServiceEnvironmentSkuCapacity
        resource_type: str
        sku: IntegrationServiceEnvironmentSkuDefinitionSku

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                capacity: Optional[IntegrationServiceEnvironmentSkuCapacity] = ..., 
                resource_type: Optional[str] = ..., 
                sku: Optional[IntegrationServiceEnvironmentSkuDefinitionSku] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSkuDefinitionSku(Model):
        name: Union[str, IntegrationServiceEnvironmentSkuName]
        tier: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[Union[str, IntegrationServiceEnvironmentSkuName]] = ..., 
                tier: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSkuList(Model):
        next_link: str
        value: list[IntegrationServiceEnvironmentSkuDefinition]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[IntegrationServiceEnvironmentSkuDefinition]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVELOPER = "Developer"
        NOT_SPECIFIED = "NotSpecified"
        PREMIUM = "Premium"


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSkuScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.logic.models.IntegrationServiceEnvironmentSubnetNetworkHealth(Model):
        network_dependency_health_state: Union[str, IntegrationServiceEnvironmentNetworkEndPointAccessibilityState]
        outbound_network_dependencies: list[IntegrationServiceEnvironmentNetworkDependency]
        outbound_network_health: IntegrationServiceEnvironmentNetworkDependencyHealth

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                network_dependency_health_state: Union[str, IntegrationServiceEnvironmentNetworkEndPointAccessibilityState], 
                outbound_network_dependencies: Optional[List[IntegrationServiceEnvironmentNetworkDependency]] = ..., 
                outbound_network_health: Optional[IntegrationServiceEnvironmentNetworkDependencyHealth] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IpAddress(Model):
        address: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.IpAddressRange(Model):
        address_range: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                address_range: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.JsonSchema(Model):
        content: str
        title: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                title: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.logic.models.KeyVaultKey(Model):
        attributes: KeyVaultKeyAttributes
        kid: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                attributes: Optional[KeyVaultKeyAttributes] = ..., 
                kid: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.KeyVaultKeyAttributes(Model):
        created: int
        enabled: bool
        updated: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created: Optional[int] = ..., 
                enabled: Optional[bool] = ..., 
                updated: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.KeyVaultKeyCollection(Model):
        skip_token: str
        value: list[KeyVaultKey]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                value: Optional[List[KeyVaultKey]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.KeyVaultKeyReference(Model):
        key_name: str
        key_vault: KeyVaultKeyReferenceKeyVault
        key_version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key_name: str, 
                key_vault: KeyVaultKeyReferenceKeyVault, 
                key_version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.KeyVaultKeyReferenceKeyVault(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.KeyVaultReference(ResourceReference):
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ListKeyVaultKeysDefinition(Model):
        key_vault: KeyVaultReference
        skip_token: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key_vault: KeyVaultReference, 
                skip_token: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ManagedApi(Resource):
        id: str
        location: str
        name: str
        properties: ApiResourceProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ApiResourceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ManagedApiListResult(Model):
        next_link: str
        value: list[ManagedApi]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ManagedApi]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.logic.models.MapType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIQUID = "Liquid"
        NOT_SPECIFIED = "NotSpecified"
        XSLT = "Xslt"
        XSLT20 = "Xslt20"
        XSLT30 = "Xslt30"


    class azure.mgmt.logic.models.MessageFilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        INCLUDE = "Include"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.NetworkConfiguration(Model):
        access_endpoint: IntegrationServiceEnvironmentAccessEndpoint
        subnets: list[ResourceReference]
        virtual_network_address_space: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_endpoint: Optional[IntegrationServiceEnvironmentAccessEndpoint] = ..., 
                subnets: Optional[List[ResourceReference]] = ..., 
                virtual_network_address_space: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OpenAuthenticationAccessPolicies(Model):
        policies: dict[str, OpenAuthenticationAccessPolicy]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                policies: Optional[Dict[str, OpenAuthenticationAccessPolicy]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OpenAuthenticationAccessPolicy(Model):
        claims: list[OpenAuthenticationPolicyClaim]
        type: Union[str, OpenAuthenticationProviderType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                claims: Optional[List[OpenAuthenticationPolicyClaim]] = ..., 
                type: Optional[Union[str, OpenAuthenticationProviderType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OpenAuthenticationPolicyClaim(Model):
        name: str
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OpenAuthenticationProviderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"


    class azure.mgmt.logic.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Operation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OperationResult(OperationResultProperties):
        code: str
        correlation: RunActionCorrelation
        end_time: datetime
        error: any
        inputs: JSON
        inputs_link: ContentLink
        iteration_count: int
        outputs: JSON
        outputs_link: ContentLink
        retry_history: list[RetryHistory]
        start_time: datetime
        status: Union[str, WorkflowStatus]
        tracked_properties: JSON
        tracking_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                correlation: Optional[RunActionCorrelation] = ..., 
                end_time: Optional[datetime] = ..., 
                error: Optional[Any] = ..., 
                iteration_count: Optional[int] = ..., 
                retry_history: Optional[List[RetryHistory]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.OperationResultProperties(Model):
        code: str
        correlation: RunActionCorrelation
        end_time: datetime
        error: any
        start_time: datetime
        status: Union[str, WorkflowStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                correlation: Optional[RunActionCorrelation] = ..., 
                end_time: Optional[datetime] = ..., 
                error: Optional[Any] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        BOOL = "Bool"
        FLOAT = "Float"
        INT = "Int"
        NOT_SPECIFIED = "NotSpecified"
        OBJECT = "Object"
        SECURE_OBJECT = "SecureObject"
        SECURE_STRING = "SecureString"
        STRING = "String"


    class azure.mgmt.logic.models.PartnerContent(Model):
        b2_b: B2BPartnerContent

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                b2_b: Optional[B2BPartnerContent] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.PartnerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        B2_B = "B2B"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.RecurrenceFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        HOUR = "Hour"
        MINUTE = "Minute"
        MONTH = "Month"
        NOT_SPECIFIED = "NotSpecified"
        SECOND = "Second"
        WEEK = "Week"
        YEAR = "Year"


    class azure.mgmt.logic.models.RecurrenceSchedule(Model):
        hours: list[int]
        minutes: list[int]
        month_days: list[int]
        monthly_occurrences: list[RecurrenceScheduleOccurrence]
        week_days: Union[list[str, DaysOfWeek]]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                hours: Optional[List[int]] = ..., 
                minutes: Optional[List[int]] = ..., 
                month_days: Optional[List[int]] = ..., 
                monthly_occurrences: Optional[List[RecurrenceScheduleOccurrence]] = ..., 
                week_days: Optional[List[Union[str, DaysOfWeek]]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RecurrenceScheduleOccurrence(Model):
        day: Union[str, DayOfWeek]
        occurrence: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                day: Optional[Union[str, DayOfWeek]] = ..., 
                occurrence: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RegenerateActionParameter(Model):
        key_type: Union[str, KeyType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                key_type: Optional[Union[str, KeyType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RepetitionIndex(Model):
        item_index: int
        scope_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                item_index: int, 
                scope_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.Request(Model):
        headers: JSON
        method: str
        uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                headers: Optional[JSON] = ..., 
                method: Optional[str] = ..., 
                uri: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RequestHistory(Resource):
        id: str
        location: str
        name: str
        properties: RequestHistoryProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[RequestHistoryProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RequestHistoryListResult(Model):
        next_link: str
        value: list[RequestHistory]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[RequestHistory]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RequestHistoryProperties(Model):
        end_time: datetime
        request: Request
        response: Response
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                request: Optional[Request] = ..., 
                response: Optional[Response] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.Resource(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.ResourceReference(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.Response(Model):
        body_link: ContentLink
        headers: JSON
        status_code: int

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                body_link: Optional[ContentLink] = ..., 
                headers: Optional[JSON] = ..., 
                status_code: Optional[int] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RetryHistory(Model):
        client_request_id: str
        code: str
        end_time: datetime
        error: ErrorResponse
        service_request_id: str
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                client_request_id: Optional[str] = ..., 
                code: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorResponse] = ..., 
                service_request_id: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RunActionCorrelation(RunCorrelation):
        action_tracking_id: str
        client_keywords: list[str]
        client_tracking_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                action_tracking_id: Optional[str] = ..., 
                client_keywords: Optional[List[str]] = ..., 
                client_tracking_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.RunCorrelation(Model):
        client_keywords: list[str]
        client_tracking_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                client_keywords: Optional[List[str]] = ..., 
                client_tracking_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        XML = "Xml"


    class azure.mgmt.logic.models.SegmentTerminatorSuffix(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CR = "CR"
        CRLF = "CRLF"
        LF = "LF"
        NONE = "None"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.SetTriggerStateActionDefinition(Model):
        source: WorkflowTriggerReference

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                source: WorkflowTriggerReference, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SigningAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        NOT_SPECIFIED = "NotSpecified"
        SHA1 = "SHA1"
        SHA2256 = "SHA2256"
        SHA2384 = "SHA2384"
        SHA2512 = "SHA2512"


    class azure.mgmt.logic.models.Sku(Model):
        name: Union[str, SkuName]
        plan: ResourceReference

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Union[str, SkuName], 
                plan: Optional[ResourceReference] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        NOT_SPECIFIED = "NotSpecified"
        PREMIUM = "Premium"
        SHARED = "Shared"
        STANDARD = "Standard"


    class azure.mgmt.logic.models.StatusAnnotation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        PREVIEW = "Preview"
        PRODUCTION = "Production"


    class azure.mgmt.logic.models.SubResource(Model):
        id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerCustomDynamicList(Model):
        built_in_operation: str
        item_title_path: str
        item_value_path: str
        items_path: str
        operation_id: str
        parameters: dict[str, SwaggerCustomDynamicProperties]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                built_in_operation: Optional[str] = ..., 
                item_title_path: Optional[str] = ..., 
                item_value_path: Optional[str] = ..., 
                items_path: Optional[str] = ..., 
                operation_id: Optional[str] = ..., 
                parameters: Optional[Dict[str, SwaggerCustomDynamicProperties]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerCustomDynamicProperties(Model):
        operation_id: str
        parameters: dict[str, SwaggerCustomDynamicProperties]
        value_path: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                parameters: Optional[Dict[str, SwaggerCustomDynamicProperties]] = ..., 
                value_path: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerCustomDynamicSchema(Model):
        operation_id: str
        parameters: dict[str, JSON]
        value_path: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                operation_id: Optional[str] = ..., 
                parameters: Optional[Dict[str, JSON]] = ..., 
                value_path: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerCustomDynamicTree(Model):
        browse: SwaggerCustomDynamicTreeCommand
        open: SwaggerCustomDynamicTreeCommand
        settings: SwaggerCustomDynamicTreeSettings

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                browse: Optional[SwaggerCustomDynamicTreeCommand] = ..., 
                open: Optional[SwaggerCustomDynamicTreeCommand] = ..., 
                settings: Optional[SwaggerCustomDynamicTreeSettings] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerCustomDynamicTreeCommand(Model):
        item_full_title_path: str
        item_is_parent: str
        item_title_path: str
        item_value_path: str
        items_path: str
        operation_id: str
        parameters: dict[str, SwaggerCustomDynamicTreeParameter]
        selectable_filter: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                item_full_title_path: Optional[str] = ..., 
                item_is_parent: Optional[str] = ..., 
                item_title_path: Optional[str] = ..., 
                item_value_path: Optional[str] = ..., 
                items_path: Optional[str] = ..., 
                operation_id: Optional[str] = ..., 
                parameters: Optional[Dict[str, SwaggerCustomDynamicTreeParameter]] = ..., 
                selectable_filter: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerCustomDynamicTreeParameter(Model):
        parameter_reference: str
        required: bool
        selected_item_value_path: str
        value: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                parameter_reference: Optional[str] = ..., 
                required: Optional[bool] = ..., 
                selected_item_value_path: Optional[str] = ..., 
                value: Optional[JSON] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerCustomDynamicTreeSettings(Model):
        can_select_leaf_nodes: bool
        can_select_parent_nodes: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                can_select_leaf_nodes: Optional[bool] = ..., 
                can_select_parent_nodes: Optional[bool] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerExternalDocumentation(Model):
        description: str
        extensions: dict[str, JSON]
        uri: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                extensions: Optional[Dict[str, JSON]] = ..., 
                uri: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerSchema(Model):
        additional_properties: JSON
        all_of: list[SwaggerSchema]
        discriminator: str
        dynamic_list_new: SwaggerCustomDynamicList
        dynamic_schema_new: SwaggerCustomDynamicProperties
        dynamic_schema_old: SwaggerCustomDynamicSchema
        dynamic_tree: SwaggerCustomDynamicTree
        example: JSON
        external_docs: SwaggerExternalDocumentation
        items: SwaggerSchema
        max_properties: int
        min_properties: int
        notification_url_extension: bool
        properties: dict[str, SwaggerSchema]
        read_only: bool
        ref: str
        required: list[str]
        title: str
        type: Union[str, SwaggerSchemaType]
        xml: SwaggerXml

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[JSON] = ..., 
                all_of: Optional[List[SwaggerSchema]] = ..., 
                discriminator: Optional[str] = ..., 
                dynamic_list_new: Optional[SwaggerCustomDynamicList] = ..., 
                dynamic_schema_new: Optional[SwaggerCustomDynamicProperties] = ..., 
                dynamic_schema_old: Optional[SwaggerCustomDynamicSchema] = ..., 
                dynamic_tree: Optional[SwaggerCustomDynamicTree] = ..., 
                example: Optional[JSON] = ..., 
                external_docs: Optional[SwaggerExternalDocumentation] = ..., 
                items: Optional[SwaggerSchema] = ..., 
                max_properties: Optional[int] = ..., 
                min_properties: Optional[int] = ..., 
                notification_url_extension: Optional[bool] = ..., 
                properties: Optional[Dict[str, SwaggerSchema]] = ..., 
                read_only: Optional[bool] = ..., 
                ref: Optional[str] = ..., 
                required: Optional[List[str]] = ..., 
                title: Optional[str] = ..., 
                type: Optional[Union[str, SwaggerSchemaType]] = ..., 
                xml: Optional[SwaggerXml] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.SwaggerSchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        FILE = "File"
        INTEGER = "Integer"
        NULL = "Null"
        NUMBER = "Number"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.logic.models.SwaggerXml(Model):
        attribute: bool
        extensions: dict[str, JSON]
        name: str
        namespace: str
        prefix: str
        wrapped: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                attribute: Optional[bool] = ..., 
                extensions: Optional[Dict[str, JSON]] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                prefix: Optional[str] = ..., 
                wrapped: Optional[bool] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.TrackEventsOperationOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE_SOURCE_INFO_ENRICH = "DisableSourceInfoEnrich"
        NONE = "None"


    class azure.mgmt.logic.models.TrackingEvent(Model):
        error: TrackingEventErrorInfo
        event_level: Union[str, EventLevel]
        event_time: datetime
        record: JSON
        record_type: Union[str, TrackingRecordType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[TrackingEventErrorInfo] = ..., 
                event_level: Union[str, EventLevel], 
                event_time: datetime, 
                record: Optional[JSON] = ..., 
                record_type: Union[str, TrackingRecordType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.TrackingEventErrorInfo(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.TrackingEventsDefinition(Model):
        events: list[TrackingEvent]
        source_type: str
        track_events_options: Union[str, TrackEventsOperationOptions]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                events: List[TrackingEvent], 
                source_type: str, 
                track_events_options: Optional[Union[str, TrackEventsOperationOptions]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.TrackingRecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AS2_MDN = "AS2MDN"
        AS2_MESSAGE = "AS2Message"
        CUSTOM = "Custom"
        EDIFACT_FUNCTIONAL_GROUP = "EdifactFunctionalGroup"
        EDIFACT_FUNCTIONAL_GROUP_ACKNOWLEDGMENT = "EdifactFunctionalGroupAcknowledgment"
        EDIFACT_INTERCHANGE = "EdifactInterchange"
        EDIFACT_INTERCHANGE_ACKNOWLEDGMENT = "EdifactInterchangeAcknowledgment"
        EDIFACT_TRANSACTION_SET = "EdifactTransactionSet"
        EDIFACT_TRANSACTION_SET_ACKNOWLEDGMENT = "EdifactTransactionSetAcknowledgment"
        NOT_SPECIFIED = "NotSpecified"
        X12_FUNCTIONAL_GROUP = "X12FunctionalGroup"
        X12_FUNCTIONAL_GROUP_ACKNOWLEDGMENT = "X12FunctionalGroupAcknowledgment"
        X12_INTERCHANGE = "X12Interchange"
        X12_INTERCHANGE_ACKNOWLEDGMENT = "X12InterchangeAcknowledgment"
        X12_TRANSACTION_SET = "X12TransactionSet"
        X12_TRANSACTION_SET_ACKNOWLEDGMENT = "X12TransactionSetAcknowledgment"


    class azure.mgmt.logic.models.TrailingSeparatorPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANDATORY = "Mandatory"
        NOT_ALLOWED = "NotAllowed"
        NOT_SPECIFIED = "NotSpecified"
        OPTIONAL = "Optional"


    class azure.mgmt.logic.models.UsageIndicator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INFORMATION = "Information"
        NOT_SPECIFIED = "NotSpecified"
        PRODUCTION = "Production"
        TEST = "Test"


    class azure.mgmt.logic.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.Workflow(Resource):
        access_control: FlowAccessControlConfiguration
        access_endpoint: str
        changed_time: datetime
        created_time: datetime
        definition: JSON
        endpoints_configuration: FlowEndpointsConfiguration
        id: str
        identity: ManagedServiceIdentity
        integration_account: ResourceReference
        integration_service_environment: ResourceReference
        location: str
        name: str
        parameters: dict[str, WorkflowParameter]
        provisioning_state: Union[str, WorkflowProvisioningState]
        sku: Sku
        state: Union[str, WorkflowState]
        tags: dict[str, str]
        type: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_control: Optional[FlowAccessControlConfiguration] = ..., 
                definition: Optional[JSON] = ..., 
                endpoints_configuration: Optional[FlowEndpointsConfiguration] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                integration_account: Optional[ResourceReference] = ..., 
                integration_service_environment: Optional[ResourceReference] = ..., 
                location: Optional[str] = ..., 
                parameters: Optional[Dict[str, WorkflowParameter]] = ..., 
                state: Optional[Union[str, WorkflowState]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowFilter(Model):
        state: Union[str, WorkflowState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, WorkflowState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowListResult(Model):
        next_link: str
        value: list[Workflow]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Workflow]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowOutputParameter(WorkflowParameter):
        description: str
        error: JSON
        metadata: JSON
        type: Union[str, ParameterType]
        value: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                metadata: Optional[JSON] = ..., 
                type: Optional[Union[str, ParameterType]] = ..., 
                value: Optional[JSON] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowParameter(Model):
        description: str
        metadata: JSON
        type: Union[str, ParameterType]
        value: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                metadata: Optional[JSON] = ..., 
                type: Optional[Union[str, ParameterType]] = ..., 
                value: Optional[JSON] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        CREATED = "Created"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        PENDING = "Pending"
        READY = "Ready"
        REGISTERED = "Registered"
        REGISTERING = "Registering"
        RENEWING = "Renewing"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNREGISTERED = "Unregistered"
        UNREGISTERING = "Unregistering"
        UPDATING = "Updating"
        WAITING = "Waiting"


    class azure.mgmt.logic.models.WorkflowReference(ResourceReference):
        id: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRun(SubResource):
        code: str
        correlation: Correlation
        correlation_id: str
        end_time: datetime
        error: JSON
        id: str
        name: str
        outputs: dict[str, WorkflowOutputParameter]
        response: WorkflowRunTrigger
        start_time: datetime
        status: Union[str, WorkflowStatus]
        trigger: WorkflowRunTrigger
        type: str
        wait_end_time: datetime
        workflow: ResourceReference

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                correlation: Optional[Correlation] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunAction(SubResource):
        code: str
        correlation: RunActionCorrelation
        end_time: datetime
        error: JSON
        id: str
        inputs_link: ContentLink
        name: str
        outputs_link: ContentLink
        retry_history: list[RetryHistory]
        start_time: datetime
        status: Union[str, WorkflowStatus]
        tracked_properties: JSON
        tracking_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                correlation: Optional[RunActionCorrelation] = ..., 
                retry_history: Optional[List[RetryHistory]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunActionFilter(Model):
        status: Union[str, WorkflowStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunActionListResult(Model):
        next_link: str
        value: list[WorkflowRunAction]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[WorkflowRunAction]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunActionRepetitionDefinition(Resource):
        code: str
        correlation: RunActionCorrelation
        end_time: datetime
        error: any
        id: str
        inputs: JSON
        inputs_link: ContentLink
        iteration_count: int
        location: str
        name: str
        outputs: JSON
        outputs_link: ContentLink
        repetition_indexes: list[RepetitionIndex]
        retry_history: list[RetryHistory]
        start_time: datetime
        status: Union[str, WorkflowStatus]
        tags: dict[str, str]
        tracked_properties: JSON
        tracking_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                correlation: Optional[RunActionCorrelation] = ..., 
                end_time: Optional[datetime] = ..., 
                error: Optional[Any] = ..., 
                iteration_count: Optional[int] = ..., 
                location: Optional[str] = ..., 
                repetition_indexes: Optional[List[RepetitionIndex]] = ..., 
                retry_history: Optional[List[RetryHistory]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunActionRepetitionDefinitionCollection(Model):
        next_link: str
        value: list[WorkflowRunActionRepetitionDefinition]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[WorkflowRunActionRepetitionDefinition]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunActionRepetitionProperties(OperationResult):
        code: str
        correlation: RunActionCorrelation
        end_time: datetime
        error: any
        inputs: JSON
        inputs_link: ContentLink
        iteration_count: int
        outputs: JSON
        outputs_link: ContentLink
        repetition_indexes: list[RepetitionIndex]
        retry_history: list[RetryHistory]
        start_time: datetime
        status: Union[str, WorkflowStatus]
        tracked_properties: JSON
        tracking_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                correlation: Optional[RunActionCorrelation] = ..., 
                end_time: Optional[datetime] = ..., 
                error: Optional[Any] = ..., 
                iteration_count: Optional[int] = ..., 
                repetition_indexes: Optional[List[RepetitionIndex]] = ..., 
                retry_history: Optional[List[RetryHistory]] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunFilter(Model):
        status: Union[str, WorkflowStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunListResult(Model):
        next_link: str
        value: list[WorkflowRun]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[WorkflowRun]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowRunTrigger(Model):
        code: str
        correlation: Correlation
        end_time: datetime
        error: JSON
        inputs: JSON
        inputs_link: ContentLink
        name: str
        outputs: JSON
        outputs_link: ContentLink
        scheduled_time: datetime
        start_time: datetime
        status: Union[str, WorkflowStatus]
        tracked_properties: JSON
        tracking_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                correlation: Optional[Correlation] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        DELETED = "Deleted"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"
        SUSPENDED = "Suspended"


    class azure.mgmt.logic.models.WorkflowStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABORTED = "Aborted"
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        FAULTED = "Faulted"
        IGNORED = "Ignored"
        NOT_SPECIFIED = "NotSpecified"
        PAUSED = "Paused"
        RUNNING = "Running"
        SKIPPED = "Skipped"
        SUCCEEDED = "Succeeded"
        SUSPENDED = "Suspended"
        TIMED_OUT = "TimedOut"
        WAITING = "Waiting"


    class azure.mgmt.logic.models.WorkflowTrigger(SubResource):
        changed_time: datetime
        created_time: datetime
        id: str
        last_execution_time: datetime
        name: str
        next_execution_time: datetime
        provisioning_state: Union[str, WorkflowTriggerProvisioningState]
        recurrence: WorkflowTriggerRecurrence
        state: Union[str, WorkflowState]
        status: Union[str, WorkflowStatus]
        type: str
        workflow: ResourceReference

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerCallbackUrl(Model):
        base_path: str
        method: str
        queries: WorkflowTriggerListCallbackUrlQueries
        relative_path: str
        relative_path_parameters: list[str]
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                queries: Optional[WorkflowTriggerListCallbackUrlQueries] = ..., 
                relative_path_parameters: Optional[List[str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerFilter(Model):
        state: Union[str, WorkflowState]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                state: Optional[Union[str, WorkflowState]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerHistory(SubResource):
        code: str
        correlation: Correlation
        end_time: datetime
        error: JSON
        fired: bool
        id: str
        inputs_link: ContentLink
        name: str
        outputs_link: ContentLink
        run: ResourceReference
        scheduled_time: datetime
        start_time: datetime
        status: Union[str, WorkflowStatus]
        tracking_id: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                correlation: Optional[Correlation] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerHistoryFilter(Model):
        status: Union[str, WorkflowStatus]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                status: Optional[Union[str, WorkflowStatus]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerHistoryListResult(Model):
        next_link: str
        value: list[WorkflowTriggerHistory]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[WorkflowTriggerHistory]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerListCallbackUrlQueries(Model):
        api_version: str
        se: str
        sig: str
        sp: str
        sv: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                se: Optional[str] = ..., 
                sig: Optional[str] = ..., 
                sp: Optional[str] = ..., 
                sv: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerListResult(Model):
        next_link: str
        value: list[WorkflowTrigger]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[WorkflowTrigger]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        CREATED = "Created"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        READY = "Ready"
        REGISTERED = "Registered"
        REGISTERING = "Registering"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNREGISTERED = "Unregistered"
        UNREGISTERING = "Unregistering"
        UPDATING = "Updating"


    class azure.mgmt.logic.models.WorkflowTriggerRecurrence(Model):
        end_time: str
        frequency: Union[str, RecurrenceFrequency]
        interval: int
        schedule: RecurrenceSchedule
        start_time: str
        time_zone: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                frequency: Optional[Union[str, RecurrenceFrequency]] = ..., 
                interval: Optional[int] = ..., 
                schedule: Optional[RecurrenceSchedule] = ..., 
                start_time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowTriggerReference(ResourceReference):
        flow_name: str
        id: str
        name: str
        trigger_name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                flow_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                trigger_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowVersion(Resource):
        access_control: FlowAccessControlConfiguration
        access_endpoint: str
        changed_time: datetime
        created_time: datetime
        definition: JSON
        endpoints_configuration: FlowEndpointsConfiguration
        id: str
        integration_account: ResourceReference
        location: str
        name: str
        parameters: dict[str, WorkflowParameter]
        provisioning_state: Union[str, WorkflowProvisioningState]
        sku: Sku
        state: Union[str, WorkflowState]
        tags: dict[str, str]
        type: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                access_control: Optional[FlowAccessControlConfiguration] = ..., 
                definition: Optional[JSON] = ..., 
                endpoints_configuration: Optional[FlowEndpointsConfiguration] = ..., 
                integration_account: Optional[ResourceReference] = ..., 
                location: Optional[str] = ..., 
                parameters: Optional[Dict[str, WorkflowParameter]] = ..., 
                state: Optional[Union[str, WorkflowState]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WorkflowVersionListResult(Model):
        next_link: str
        value: list[WorkflowVersion]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[WorkflowVersion]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.WsdlImportMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        SOAP_PASS_THROUGH = "SoapPassThrough"
        SOAP_TO_REST = "SoapToRest"


    class azure.mgmt.logic.models.WsdlService(Model):
        endpoint_qualified_names: list[str]
        qualified_name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                endpoint_qualified_names: Optional[List[str]] = ..., 
                qualified_name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12AcknowledgementSettings(Model):
        acknowledgement_control_number_lower_bound: int
        acknowledgement_control_number_prefix: str
        acknowledgement_control_number_suffix: str
        acknowledgement_control_number_upper_bound: int
        batch_functional_acknowledgements: bool
        batch_implementation_acknowledgements: bool
        batch_technical_acknowledgements: bool
        functional_acknowledgement_version: str
        implementation_acknowledgement_version: str
        need_functional_acknowledgement: bool
        need_implementation_acknowledgement: bool
        need_loop_for_valid_messages: bool
        need_technical_acknowledgement: bool
        rollover_acknowledgement_control_number: bool
        send_synchronous_acknowledgement: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                acknowledgement_control_number_lower_bound: int, 
                acknowledgement_control_number_prefix: Optional[str] = ..., 
                acknowledgement_control_number_suffix: Optional[str] = ..., 
                acknowledgement_control_number_upper_bound: int, 
                batch_functional_acknowledgements: bool, 
                batch_implementation_acknowledgements: bool, 
                batch_technical_acknowledgements: bool, 
                functional_acknowledgement_version: Optional[str] = ..., 
                implementation_acknowledgement_version: Optional[str] = ..., 
                need_functional_acknowledgement: bool, 
                need_implementation_acknowledgement: bool, 
                need_loop_for_valid_messages: bool, 
                need_technical_acknowledgement: bool, 
                rollover_acknowledgement_control_number: bool, 
                send_synchronous_acknowledgement: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12AgreementContent(Model):
        receive_agreement: X12OneWayAgreement
        send_agreement: X12OneWayAgreement

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                receive_agreement: X12OneWayAgreement, 
                send_agreement: X12OneWayAgreement, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12CharacterSet(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        EXTENDED = "Extended"
        NOT_SPECIFIED = "NotSpecified"
        UTF8 = "UTF8"


    class azure.mgmt.logic.models.X12DateFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CCYYMMDD = "CCYYMMDD"
        NOT_SPECIFIED = "NotSpecified"
        YYMMDD = "YYMMDD"


    class azure.mgmt.logic.models.X12DelimiterOverrides(Model):
        component_separator: int
        data_element_separator: int
        message_id: str
        protocol_version: str
        replace_character: int
        replace_separators_in_payload: bool
        segment_terminator: int
        segment_terminator_suffix: Union[str, SegmentTerminatorSuffix]
        target_namespace: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                component_separator: int, 
                data_element_separator: int, 
                message_id: Optional[str] = ..., 
                protocol_version: Optional[str] = ..., 
                replace_character: int, 
                replace_separators_in_payload: bool, 
                segment_terminator: int, 
                segment_terminator_suffix: Union[str, SegmentTerminatorSuffix], 
                target_namespace: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12EnvelopeOverride(Model):
        date_format: Union[str, X12DateFormat]
        functional_identifier_code: str
        header_version: str
        message_id: str
        protocol_version: str
        receiver_application_id: str
        responsible_agency_code: str
        sender_application_id: str
        target_namespace: str
        time_format: Union[str, X12TimeFormat]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                date_format: Union[str, X12DateFormat], 
                functional_identifier_code: Optional[str] = ..., 
                header_version: str, 
                message_id: str, 
                protocol_version: str, 
                receiver_application_id: str, 
                responsible_agency_code: str, 
                sender_application_id: str, 
                target_namespace: str, 
                time_format: Union[str, X12TimeFormat], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12EnvelopeSettings(Model):
        control_standards_id: int
        control_version_number: str
        enable_default_group_headers: bool
        functional_group_id: str
        group_control_number_lower_bound: int
        group_control_number_upper_bound: int
        group_header_agency_code: str
        group_header_date_format: Union[str, X12DateFormat]
        group_header_time_format: Union[str, X12TimeFormat]
        group_header_version: str
        interchange_control_number_lower_bound: int
        interchange_control_number_upper_bound: int
        overwrite_existing_transaction_set_control_number: bool
        receiver_application_id: str
        rollover_group_control_number: bool
        rollover_interchange_control_number: bool
        rollover_transaction_set_control_number: bool
        sender_application_id: str
        transaction_set_control_number_lower_bound: int
        transaction_set_control_number_prefix: str
        transaction_set_control_number_suffix: str
        transaction_set_control_number_upper_bound: int
        usage_indicator: Union[str, UsageIndicator]
        use_control_standards_id_as_repetition_character: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                control_standards_id: int, 
                control_version_number: str, 
                enable_default_group_headers: bool, 
                functional_group_id: Optional[str] = ..., 
                group_control_number_lower_bound: int, 
                group_control_number_upper_bound: int, 
                group_header_agency_code: str, 
                group_header_date_format: Union[str, X12DateFormat], 
                group_header_time_format: Union[str, X12TimeFormat], 
                group_header_version: str, 
                interchange_control_number_lower_bound: int, 
                interchange_control_number_upper_bound: int, 
                overwrite_existing_transaction_set_control_number: bool, 
                receiver_application_id: str, 
                rollover_group_control_number: bool, 
                rollover_interchange_control_number: bool, 
                rollover_transaction_set_control_number: bool, 
                sender_application_id: str, 
                transaction_set_control_number_lower_bound: int, 
                transaction_set_control_number_prefix: Optional[str] = ..., 
                transaction_set_control_number_suffix: Optional[str] = ..., 
                transaction_set_control_number_upper_bound: int, 
                usage_indicator: Union[str, UsageIndicator], 
                use_control_standards_id_as_repetition_character: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12FramingSettings(Model):
        character_set: Union[str, X12CharacterSet]
        component_separator: int
        data_element_separator: int
        replace_character: int
        replace_separators_in_payload: bool
        segment_terminator: int
        segment_terminator_suffix: Union[str, SegmentTerminatorSuffix]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                character_set: Union[str, X12CharacterSet], 
                component_separator: int, 
                data_element_separator: int, 
                replace_character: int, 
                replace_separators_in_payload: bool, 
                segment_terminator: int, 
                segment_terminator_suffix: Union[str, SegmentTerminatorSuffix], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12MessageFilter(Model):
        message_filter_type: Union[str, MessageFilterType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                message_filter_type: Union[str, MessageFilterType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12MessageIdentifier(Model):
        message_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                message_id: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12OneWayAgreement(Model):
        protocol_settings: X12ProtocolSettings
        receiver_business_identity: BusinessIdentity
        sender_business_identity: BusinessIdentity

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                protocol_settings: X12ProtocolSettings, 
                receiver_business_identity: BusinessIdentity, 
                sender_business_identity: BusinessIdentity, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12ProcessingSettings(Model):
        convert_implied_decimal: bool
        create_empty_xml_tags_for_trailing_separators: bool
        mask_security_info: bool
        preserve_interchange: bool
        suspend_interchange_on_error: bool
        use_dot_as_decimal_separator: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                convert_implied_decimal: bool, 
                create_empty_xml_tags_for_trailing_separators: bool, 
                mask_security_info: bool, 
                preserve_interchange: bool, 
                suspend_interchange_on_error: bool, 
                use_dot_as_decimal_separator: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12ProtocolSettings(Model):
        acknowledgement_settings: X12AcknowledgementSettings
        envelope_overrides: list[X12EnvelopeOverride]
        envelope_settings: X12EnvelopeSettings
        framing_settings: X12FramingSettings
        message_filter: X12MessageFilter
        message_filter_list: list[X12MessageIdentifier]
        processing_settings: X12ProcessingSettings
        schema_references: list[X12SchemaReference]
        security_settings: X12SecuritySettings
        validation_overrides: list[X12ValidationOverride]
        validation_settings: X12ValidationSettings
        x12_delimiter_overrides: list[X12DelimiterOverrides]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                acknowledgement_settings: X12AcknowledgementSettings, 
                envelope_overrides: Optional[List[X12EnvelopeOverride]] = ..., 
                envelope_settings: X12EnvelopeSettings, 
                framing_settings: X12FramingSettings, 
                message_filter: X12MessageFilter, 
                message_filter_list: Optional[List[X12MessageIdentifier]] = ..., 
                processing_settings: X12ProcessingSettings, 
                schema_references: List[X12SchemaReference], 
                security_settings: X12SecuritySettings, 
                validation_overrides: Optional[List[X12ValidationOverride]] = ..., 
                validation_settings: X12ValidationSettings, 
                x12_delimiter_overrides: Optional[List[X12DelimiterOverrides]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12SchemaReference(Model):
        message_id: str
        schema_name: str
        schema_version: str
        sender_application_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                message_id: str, 
                schema_name: str, 
                schema_version: str, 
                sender_application_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12SecuritySettings(Model):
        authorization_qualifier: str
        authorization_value: str
        password_value: str
        security_qualifier: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                authorization_qualifier: str, 
                authorization_value: Optional[str] = ..., 
                password_value: Optional[str] = ..., 
                security_qualifier: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12TimeFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HHMM = "HHMM"
        HHMMSS = "HHMMSS"
        HHMMS_SD = "HHMMSSd"
        HHMMS_SDD = "HHMMSSdd"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.logic.models.X12ValidationOverride(Model):
        allow_leading_and_trailing_spaces_and_zeroes: bool
        message_id: str
        trailing_separator_policy: Union[str, TrailingSeparatorPolicy]
        trim_leading_and_trailing_spaces_and_zeroes: bool
        validate_character_set: bool
        validate_edi_types: bool
        validate_xsd_types: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allow_leading_and_trailing_spaces_and_zeroes: bool, 
                message_id: str, 
                trailing_separator_policy: Union[str, TrailingSeparatorPolicy], 
                trim_leading_and_trailing_spaces_and_zeroes: bool, 
                validate_character_set: bool, 
                validate_edi_types: bool, 
                validate_xsd_types: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.logic.models.X12ValidationSettings(Model):
        allow_leading_and_trailing_spaces_and_zeroes: bool
        check_duplicate_group_control_number: bool
        check_duplicate_interchange_control_number: bool
        check_duplicate_transaction_set_control_number: bool
        interchange_control_number_validity_days: int
        trailing_separator_policy: Union[str, TrailingSeparatorPolicy]
        trim_leading_and_trailing_spaces_and_zeroes: bool
        validate_character_set: bool
        validate_edi_types: bool
        validate_xsd_types: bool

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                allow_leading_and_trailing_spaces_and_zeroes: bool, 
                check_duplicate_group_control_number: bool, 
                check_duplicate_interchange_control_number: bool, 
                check_duplicate_transaction_set_control_number: bool, 
                interchange_control_number_validity_days: int, 
                trailing_separator_policy: Union[str, TrailingSeparatorPolicy], 
                trim_leading_and_trailing_spaces_and_zeroes: bool, 
                validate_character_set: bool, 
                validate_edi_types: bool, 
                validate_xsd_types: bool, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


namespace azure.mgmt.logic.operations

    class azure.mgmt.logic.operations.IntegrationAccountAgreementsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                agreement: IntegrationAccountAgreement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountAgreement: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                agreement: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountAgreement: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountAgreement: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccountAgreement]: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                agreement_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.operations.IntegrationAccountAssembliesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                assembly_artifact: AssemblyDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssemblyDefinition: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                assembly_artifact: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AssemblyDefinition: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AssemblyDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AssemblyDefinition]: ...

        @distributed_trace
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                assembly_artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.operations.IntegrationAccountBatchConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                batch_configuration: BatchConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                batch_configuration: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                batch_configuration_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BatchConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BatchConfiguration]: ...


    class azure.mgmt.logic.operations.IntegrationAccountCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                certificate: IntegrationAccountCertificate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountCertificate: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                certificate: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountCertificate: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                certificate_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccountCertificate]: ...


    class azure.mgmt.logic.operations.IntegrationAccountMapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                map: IntegrationAccountMap, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountMap: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                map: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountMap: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountMap: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccountMap]: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                map_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.operations.IntegrationAccountPartnersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                partner: IntegrationAccountPartner, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountPartner: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                partner: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountPartner: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountPartner: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccountPartner]: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                partner_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.operations.IntegrationAccountSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                schema: IntegrationAccountSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSchema: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                schema: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSchema: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountSchema: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccountSchema]: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                list_content_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        def list_content_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                schema_name: str, 
                list_content_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.operations.IntegrationAccountSessionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                session: IntegrationAccountSession, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSession: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                session: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccountSession: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                session_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccountSession: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccountSession]: ...


    class azure.mgmt.logic.operations.IntegrationAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IntegrationAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccount]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationAccount]: ...

        @overload
        def list_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                parameters: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CallbackUrl: ...

        @overload
        def list_callback_url(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CallbackUrl: ...

        @overload
        def list_key_vault_keys(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                list_key_vault_keys: ListKeyVaultKeysDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[KeyVaultKey]: ...

        @overload
        def list_key_vault_keys(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                list_key_vault_keys: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[KeyVaultKey]: ...

        @overload
        def log_tracking_events(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                log_tracking_events: TrackingEventsDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def log_tracking_events(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                log_tracking_events: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def regenerate_access_key(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                regenerate_access_key: RegenerateActionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        def regenerate_access_key(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                regenerate_access_key: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IntegrationAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                integration_account_name: str, 
                integration_account: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IntegrationAccount: ...


    class azure.mgmt.logic.operations.IntegrationServiceEnvironmentManagedApiOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ApiOperation]: ...


    class azure.mgmt.logic.operations.IntegrationServiceEnvironmentManagedApisOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_put(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                integration_service_environment_managed_api: IntegrationServiceEnvironmentManagedApi, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationServiceEnvironmentManagedApi]: ...

        @overload
        def begin_put(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                integration_service_environment_managed_api: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationServiceEnvironmentManagedApi]: ...

        @distributed_trace
        def get(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                api_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationServiceEnvironmentManagedApi: ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationServiceEnvironmentManagedApi]: ...


    class azure.mgmt.logic.operations.IntegrationServiceEnvironmentNetworkHealthOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Dict[str, IntegrationServiceEnvironmentSubnetNetworkHealth]: ...


    class azure.mgmt.logic.operations.IntegrationServiceEnvironmentSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationServiceEnvironmentSkuDefinition]: ...


    class azure.mgmt.logic.operations.IntegrationServiceEnvironmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IntegrationServiceEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationServiceEnvironment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationServiceEnvironment]: ...

        @overload
        def begin_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IntegrationServiceEnvironment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationServiceEnvironment]: ...

        @overload
        def begin_update(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                integration_service_environment: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IntegrationServiceEnvironment]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> IntegrationServiceEnvironment: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationServiceEnvironment]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[IntegrationServiceEnvironment]: ...

        @distributed_trace
        def restart(
                self, 
                resource_group: str, 
                integration_service_environment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.logic.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


    class azure.mgmt.logic.operations.WorkflowRunActionRepetitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRunActionRepetitionDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkflowRunActionRepetitionDefinition]: ...

        @distributed_trace
        def list_expression_traces(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ExpressionRoot]: ...


    class azure.mgmt.logic.operations.WorkflowRunActionRepetitionsRequestHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                request_history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RequestHistory: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RequestHistory]: ...


    class azure.mgmt.logic.operations.WorkflowRunActionRequestHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                request_history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RequestHistory: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[RequestHistory]: ...


    class azure.mgmt.logic.operations.WorkflowRunActionScopeRepetitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                repetition_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRunActionRepetitionDefinition: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkflowRunActionRepetitionDefinition]: ...


    class azure.mgmt.logic.operations.WorkflowRunActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRunAction: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkflowRunAction]: ...

        @distributed_trace
        def list_expression_traces(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                action_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ExpressionRoot]: ...


    class azure.mgmt.logic.operations.WorkflowRunOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                operation_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRun: ...


    class azure.mgmt.logic.operations.WorkflowRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def cancel(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                run_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkflowRun]: ...


    class azure.mgmt.logic.operations.WorkflowTriggerHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTriggerHistory: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkflowTriggerHistory]: ...

        @distributed_trace
        def resubmit(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                history_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.logic.operations.WorkflowTriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTrigger: ...

        @distributed_trace
        def get_schema_json(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JsonSchema: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkflowTrigger]: ...

        @distributed_trace
        def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @distributed_trace
        def reset(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def run(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_state(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                set_state: SetTriggerStateActionDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set_state(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                trigger_name: str, 
                set_state: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.logic.operations.WorkflowVersionTriggersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                version_id: str, 
                trigger_name: str, 
                parameters: Optional[GetCallbackUrlParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                version_id: str, 
                trigger_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...


    class azure.mgmt.logic.operations.WorkflowVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                version_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> WorkflowVersion: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                top: Optional[int] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[WorkflowVersion]: ...


    class azure.mgmt.logic.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_move(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                move: WorkflowReference, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_move(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                move: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                workflow: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                workflow: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def generate_upgraded_definition(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: GenerateUpgradedDefinitionParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def generate_upgraded_definition(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workflow]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Workflow]: ...

        @overload
        def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                list_callback_url: GetCallbackUrlParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @overload
        def list_callback_url(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                list_callback_url: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> WorkflowTriggerCallbackUrl: ...

        @distributed_trace
        def list_swagger(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def regenerate_access_key(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                key_type: RegenerateActionParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def regenerate_access_key(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                key_type: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Workflow: ...

        @overload
        def validate_by_location(
                self, 
                resource_group_name: str, 
                location: str, 
                workflow_name: str, 
                validate: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate_by_location(
                self, 
                resource_group_name: str, 
                location: str, 
                workflow_name: str, 
                validate: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate_by_resource_group(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                validate: Workflow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate_by_resource_group(
                self, 
                resource_group_name: str, 
                workflow_name: str, 
                validate: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


```