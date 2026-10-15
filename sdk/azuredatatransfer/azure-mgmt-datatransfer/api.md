```py
namespace azure.mgmt.datatransfer

    class azure.mgmt.datatransfer.AzureDataTransferClient: implements ContextManager 
        azure_data_transfer: AzureDataTransferOperations
        connections: ConnectionsOperations
        flow_profiles: FlowProfilesOperations
        flows: FlowsOperations
        operations: Operations
        pipelines: PipelinesOperations

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


namespace azure.mgmt.datatransfer.aio

    class azure.mgmt.datatransfer.aio.AzureDataTransferClient: implements AsyncContextManager 
        azure_data_transfer: AzureDataTransferOperations
        connections: ConnectionsOperations
        flow_profiles: FlowProfilesOperations
        flows: FlowsOperations
        operations: Operations
        pipelines: PipelinesOperations

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


namespace azure.mgmt.datatransfer.aio.operations

    class azure.mgmt.datatransfer.aio.operations.AzureDataTransferOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def list_approved_schemas(
                self, 
                pipeline: ListApprovedSchemasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        async def list_approved_schemas(
                self, 
                pipeline: ListApprovedSchemasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        async def list_approved_schemas(
                self, 
                pipeline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        async def list_flow_profiles(
                self, 
                body: ListFlowProfilesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FlowProfilesListResult: ...

        @overload
        async def list_flow_profiles(
                self, 
                body: ListFlowProfilesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FlowProfilesListResult: ...

        @overload
        async def list_flow_profiles(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FlowProfilesListResult: ...

        @overload
        async def list_pipeline_metadata(
                self, 
                body: ListPipelineMetadataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListPipelineMetadataResult: ...

        @overload
        async def list_pipeline_metadata(
                self, 
                body: ListPipelineMetadataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListPipelineMetadataResult: ...

        @overload
        async def list_pipeline_metadata(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListPipelineMetadataResult: ...

        @overload
        async def validate_schema(
                self, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSchemaResult: ...

        @overload
        async def validate_schema(
                self, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSchemaResult: ...

        @overload
        async def validate_schema(
                self, 
                schema: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSchemaResult: ...


    class azure.mgmt.datatransfer.aio.operations.ConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ConnectionsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ConnectionsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PendingConnection]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Connection]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Connection]: ...

        @distributed_trace
        def list_pending_flows_list(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PendingFlow]: ...


    class azure.mgmt.datatransfer.aio.operations.FlowProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                resource: FlowProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FlowProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                resource: FlowProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FlowProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FlowProfile]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-05-30-preview', params_added_on={'2025-05-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'pipeline_name', 'flow_profile_name']}, api_versions_list=['2025-05-30-preview', '2025-10-10-preview', '2026-02-06-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                properties: FlowProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FlowProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                properties: FlowProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FlowProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FlowProfile]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-05-30-preview', params_added_on={'2025-05-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'pipeline_name', 'flow_profile_name', 'accept']}, api_versions_list=['2025-05-30-preview', '2025-10-10-preview', '2026-02-06-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                **kwargs: Any
            ) -> FlowProfile: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-30-preview', params_added_on={'2025-05-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'pipeline_name', 'accept']}, api_versions_list=['2025-05-30-preview', '2025-10-10-preview', '2026-02-06-preview'])
        def list_by_pipeline(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FlowProfile]: ...


    class azure.mgmt.datatransfer.aio.operations.FlowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: Flow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: Flow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_disable(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @distributed_trace_async
        async def begin_enable(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @distributed_trace_async
        async def begin_generate_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoint_ports: SetDestinationEndpointPorts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoint_ports: SetDestinationEndpointPorts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoint_ports: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoints: SetDestinationEndpoints, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoints: SetDestinationEndpoints, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoints: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                passphrase: SetStreamPassphrase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                passphrase: SetStreamPassphrase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                passphrase: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                source_addresses: SetSourceAddresses, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                source_addresses: SetSourceAddresses, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_set_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                source_addresses: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Flow]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: FlowsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: FlowsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> Flow: ...

        @distributed_trace_async
        async def get_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> GetDestinationEndpointPortsResult: ...

        @distributed_trace_async
        async def get_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> GetDestinationEndpointsResult: ...

        @distributed_trace_async
        async def get_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> StreamSourceAddresses: ...

        @distributed_trace_async
        async def get_stream_connection_string(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> GetStreamConnectionStringResult: ...

        @distributed_trace
        def list_by_connection(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Flow]: ...


    class azure.mgmt.datatransfer.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.datatransfer.aio.operations.PipelinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_approve_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_approve_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_approve_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: Pipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pipeline]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: Pipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pipeline]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pipeline]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute_action(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                action: Action, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pipeline]: ...

        @overload
        async def begin_execute_action(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                action: Action, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pipeline]: ...

        @overload
        async def begin_execute_action(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                action: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pipeline]: ...

        @overload
        async def begin_reject_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_reject_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_reject_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Connection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: PipelinesPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: PipelinesPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                **kwargs: Any
            ) -> Pipeline: ...

        @overload
        async def list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connections: Optional[ConnectionIdList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListFlowsByPipelineResult: ...

        @overload
        async def list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connections: Optional[ConnectionIdList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListFlowsByPipelineResult: ...

        @overload
        async def list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connections: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListFlowsByPipelineResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Pipeline]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Pipeline]: ...

        @overload
        async def list_schemas_list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        async def list_schemas_list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        async def list_schemas_list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                schema: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...


namespace azure.mgmt.datatransfer.models

    class azure.mgmt.datatransfer.models.Action(_Model):
        action_type: Union[str, DateTransferActionType]
        justification: Optional[str]
        target_type: Union[str, TargetType]
        targets: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Union[str, DateTransferActionType], 
                justification: Optional[str] = ..., 
                target_type: Union[str, TargetType], 
                targets: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.datatransfer.models.AntivirusRuleset(_Model):
        av_solutions: Optional[list[Union[str, AntivirusSolutions]]]

        @overload
        def __init__(
                self, 
                *, 
                av_solutions: Optional[list[Union[str, AntivirusSolutions]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.AntivirusSolutions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLAM_AV = "ClamAv"
        DEFENDER = "Defender"


    class azure.mgmt.datatransfer.models.ApiFlowOptions(_Model):
        api_mode: Optional[Union[str, ApiMode]]
        audience_override: Optional[str]
        authentication: Optional[list[Authentication]]
        cname: Optional[str]
        identity_translation: Optional[Union[str, IdentityTranslation]]
        remote_calling_mode_client_id: Optional[str]
        remote_endpoint: Optional[str]
        remote_endpoint_settings: Optional[RemoteEndpointSettings]
        sender_client_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_mode: Optional[Union[str, ApiMode]] = ..., 
                audience_override: Optional[str] = ..., 
                authentication: Optional[list[Authentication]] = ..., 
                cname: Optional[str] = ..., 
                identity_translation: Optional[Union[str, IdentityTranslation]] = ..., 
                remote_calling_mode_client_id: Optional[str] = ..., 
                remote_endpoint: Optional[str] = ..., 
                remote_endpoint_settings: Optional[RemoteEndpointSettings] = ..., 
                sender_client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ApiMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENDPOINT = "Endpoint"
        SDK = "SDK"


    class azure.mgmt.datatransfer.models.ArchiveRuleset(_Model):
        maximum_compression_ratio_limit: Optional[float]
        maximum_depth_limit: Optional[int]
        maximum_expansion_size_limit: Optional[int]
        minimum_size_for_expansion: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                maximum_compression_ratio_limit: Optional[float] = ..., 
                maximum_depth_limit: Optional[int] = ..., 
                maximum_expansion_size_limit: Optional[int] = ..., 
                minimum_size_for_expansion: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.Authentication(_Model):
        application_ids: Optional[list[str]]
        audience: Optional[str]
        authority: Optional[str]
        client_id_override: Optional[str]
        identity_translation: Optional[Union[str, IdentityTranslation]]
        instance: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, AuthenticationType]]

        @overload
        def __init__(
                self, 
                *, 
                application_ids: Optional[list[str]] = ..., 
                audience: Optional[str] = ..., 
                authority: Optional[str] = ..., 
                client_id_override: Optional[str] = ..., 
                identity_translation: Optional[Union[str, IdentityTranslation]] = ..., 
                instance: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Optional[Union[str, AuthenticationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JWT = "JWT"
        NONE = "None"


    class azure.mgmt.datatransfer.models.Casing(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSENSITIVE = "Insensitive"
        SENSITIVE = "Sensitive"


    class azure.mgmt.datatransfer.models.Connection(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ConnectionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ConnectionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ConnectionIdList(_Model):
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ConnectionProperties(_Model):
        api_hostname: Optional[str]
        approver: Optional[str]
        date_submitted: Optional[datetime]
        direction: Optional[Union[str, Direction]]
        flow_profile_list: Optional[list[FlowProfileMetadata]]
        flow_types: Optional[list[Union[str, FlowType]]]
        force_disabled_status: Optional[list[Union[str, ForceDisabledStatus]]]
        justification: Optional[str]
        link_status: Optional[Union[str, LinkStatus]]
        linked_connection_id: Optional[str]
        pin: Optional[str]
        pipeline: str
        policies: Optional[list[str]]
        primary_contact: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        remote_subscription_id: Optional[str]
        requirement_id: Optional[str]
        schema_uris: Optional[list[str]]
        schemas: Optional[list[Schema]]
        secondary_contacts: Optional[list[str]]
        status: Optional[Union[str, ConnectionStatus]]
        status_reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_hostname: Optional[str] = ..., 
                direction: Optional[Union[str, Direction]] = ..., 
                flow_profile_list: Optional[list[FlowProfileMetadata]] = ..., 
                flow_types: Optional[list[Union[str, FlowType]]] = ..., 
                justification: Optional[str] = ..., 
                pin: Optional[str] = ..., 
                pipeline: str, 
                policies: Optional[list[str]] = ..., 
                primary_contact: Optional[str] = ..., 
                remote_subscription_id: Optional[str] = ..., 
                requirement_id: Optional[str] = ..., 
                schema_uris: Optional[list[str]] = ..., 
                schemas: Optional[list[Schema]] = ..., 
                secondary_contacts: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        APPROVED = "Approved"
        IN_REVIEW = "InReview"
        REJECTED = "Rejected"


    class azure.mgmt.datatransfer.models.ConnectionsPatch(_Model):
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


    class azure.mgmt.datatransfer.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.datatransfer.models.DataClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_ENDPOINT = "ApiEndpoint"
        API_SDK = "ApiSDK"
        BLOB = "Blob"
        EVENT_HUB = "EventHub"
        SERVICE_BUS = "ServiceBus"
        TABLE = "Table"
        VIDEO = "Video"


    class azure.mgmt.datatransfer.models.DataClassType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API = "API"
        COMPLEX = "Complex"
        FILES = "Files"
        MESSAGING = "Messaging"
        SOFTWARE_ARTIFACTS = "SoftwareArtifacts"
        STREAM = "Stream"


    class azure.mgmt.datatransfer.models.DataSizeRuleset(_Model):
        maximum: Optional[int]
        minimum: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                maximum: Optional[int] = ..., 
                minimum: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.DataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB = "Blob"
        TABLE = "Table"


    class azure.mgmt.datatransfer.models.DateTransferActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_UPDATES = "AllowUpdates"
        FORCE_DISABLE = "ForceDisable"


    class azure.mgmt.datatransfer.models.Direction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RECEIVE = "Receive"
        SEND = "Send"


    class azure.mgmt.datatransfer.models.DirectionSettings(_Model):
        complete_linking: Union[str, EnablementStatus]
        connection_approvals: Union[str, EnablementStatus]
        flow_approvals: Optional[Union[str, EnablementStatus]]
        flow_profile_data_classes_available: Optional[list[Union[str, DataClassType]]]
        flow_types_available: Optional[list[Union[str, FlowType]]]
        messaging_flow_type_schema_validation: Optional[Union[str, EnablementStatus]]
        messaging_flows_pricing_options: Optional[list[Union[str, FlowBillingTier]]]

        @overload
        def __init__(
                self, 
                *, 
                complete_linking: Union[str, EnablementStatus], 
                connection_approvals: Union[str, EnablementStatus], 
                flow_approvals: Optional[Union[str, EnablementStatus]] = ..., 
                flow_profile_data_classes_available: Optional[list[Union[str, DataClassType]]] = ..., 
                flow_types_available: Optional[list[Union[str, FlowType]]] = ..., 
                messaging_flow_type_schema_validation: Optional[Union[str, EnablementStatus]] = ..., 
                messaging_flows_pricing_options: Optional[list[Union[str, FlowBillingTier]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.EnablementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.datatransfer.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.datatransfer.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.datatransfer.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.datatransfer.models.Flow(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        plan: Optional[Plan]
        properties: Optional[FlowProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                plan: Optional[Plan] = ..., 
                properties: Optional[FlowProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowBillingTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_TRANSPORT = "BlobTransport"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.datatransfer.models.FlowProfile(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[FlowProfileProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[FlowProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowProfileMetadata(_Model):
        description: str
        flow_profile_id: str
        name: str
        pipeline: str
        replication_scenario: Union[str, DataClassType]
        status: Union[str, FlowProfileStatus]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                flow_profile_id: str, 
                name: str, 
                pipeline: str, 
                replication_scenario: Union[str, DataClassType], 
                status: Union[str, FlowProfileStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowProfilePatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[FlowProfilePatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[FlowProfilePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowProfilePatchProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rulesets: Optional[FlowProfileRulesets]
        status: Optional[Union[str, FlowProfileStatus]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                rulesets: Optional[FlowProfileRulesets] = ..., 
                status: Optional[Union[str, FlowProfileStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowProfileProperties(_Model):
        description: str
        flow_profile_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replication_scenario: Union[str, DataClassType]
        rulesets: Optional[FlowProfileRulesets]
        status: Union[str, FlowProfileStatus]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                replication_scenario: Union[str, DataClassType], 
                rulesets: Optional[FlowProfileRulesets] = ..., 
                status: Union[str, FlowProfileStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowProfileRulesets(_Model):
        antivirus: Optional[AntivirusRuleset]
        archives: Optional[ArchiveRuleset]
        data_size: Optional[DataSizeRuleset]
        mime_filters: Optional[MimeFilterRuleset]
        text_matching: Optional[TextMatchingRuleset]
        xml_filters: Optional[XmlFilterRuleset]

        @overload
        def __init__(
                self, 
                *, 
                antivirus: Optional[AntivirusRuleset] = ..., 
                archives: Optional[ArchiveRuleset] = ..., 
                data_size: Optional[DataSizeRuleset] = ..., 
                mime_filters: Optional[MimeFilterRuleset] = ..., 
                text_matching: Optional[TextMatchingRuleset] = ..., 
                xml_filters: Optional[XmlFilterRuleset] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowProfileStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        OBSOLETE = "Obsolete"


    class azure.mgmt.datatransfer.models.FlowProfilesListResult(_Model):
        value: Optional[list[FlowProfileMetadata]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[FlowProfileMetadata]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowProperties(_Model):
        api_flow_options: Optional[ApiFlowOptions]
        connection: Optional[SelectedResource]
        consumer_group: Optional[str]
        customer_managed_key_vault_uri: Optional[str]
        data_type: Optional[Union[str, DataType]]
        destination_endpoint_ports: Optional[list[int]]
        destination_endpoints: Optional[list[str]]
        event_hub_id: Optional[str]
        flow_data_type: Optional[Union[str, DataClass]]
        flow_id: Optional[str]
        flow_profile: Optional[FlowProfileMetadata]
        flow_type: Optional[Union[str, FlowType]]
        force_disabled_status: Optional[list[Union[str, ForceDisabledStatus]]]
        key_vault_uri: Optional[str]
        link_status: Optional[Union[str, LinkStatus]]
        linked_flow_id: Optional[str]
        messaging_options: Optional[MessagingOptions]
        passphrase: Optional[str]
        policies: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        schema: Optional[Schema]
        service_bus_queue_id: Optional[str]
        source_addresses: Optional[StreamSourceAddresses]
        status: Optional[Union[str, FlowStatus]]
        storage_account_id: Optional[str]
        storage_account_name: Optional[str]
        storage_container_name: Optional[str]
        storage_table_name: Optional[str]
        stream_id: Optional[str]
        stream_latency: Optional[int]
        stream_protocol: Optional[Union[str, StreamProtocol]]

        @overload
        def __init__(
                self, 
                *, 
                api_flow_options: Optional[ApiFlowOptions] = ..., 
                connection: Optional[SelectedResource] = ..., 
                consumer_group: Optional[str] = ..., 
                customer_managed_key_vault_uri: Optional[str] = ..., 
                data_type: Optional[Union[str, DataType]] = ..., 
                destination_endpoint_ports: Optional[list[int]] = ..., 
                destination_endpoints: Optional[list[str]] = ..., 
                event_hub_id: Optional[str] = ..., 
                flow_data_type: Optional[Union[str, DataClass]] = ..., 
                flow_profile: Optional[FlowProfileMetadata] = ..., 
                flow_type: Optional[Union[str, FlowType]] = ..., 
                key_vault_uri: Optional[str] = ..., 
                messaging_options: Optional[MessagingOptions] = ..., 
                passphrase: Optional[str] = ..., 
                policies: Optional[list[str]] = ..., 
                schema: Optional[Schema] = ..., 
                service_bus_queue_id: Optional[str] = ..., 
                source_addresses: Optional[StreamSourceAddresses] = ..., 
                status: Optional[Union[str, FlowStatus]] = ..., 
                storage_account_id: Optional[str] = ..., 
                storage_account_name: Optional[str] = ..., 
                storage_container_name: Optional[str] = ..., 
                storage_table_name: Optional[str] = ..., 
                stream_id: Optional[str] = ..., 
                stream_latency: Optional[int] = ..., 
                stream_protocol: Optional[Union[str, StreamProtocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.datatransfer.models.FlowType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API = "API"
        BASIC_FILES = "BasicFiles"
        COMPLEX = "Complex"
        DATA = "Data"
        DEV_SEC_OPS = "DevSecOps"
        DISK_IMAGES = "DiskImages"
        MESSAGING = "Messaging"
        MICROSOFT_INTERNAL = "MicrosoftInternal"
        MISSION = "Mission"
        MISSION_OPAQUE_XML = "MissionOpaqueXML"
        OPAQUE = "Opaque"
        STANDARD = "Standard"
        STREAMING_VIDEO = "StreamingVideo"
        UNKNOWN = "Unknown"


    class azure.mgmt.datatransfer.models.FlowsPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[FlowsPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[FlowsPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.FlowsPatchProperties(_Model):
        passphrase: Optional[str]
        stream_id: Optional[str]
        stream_latency: Optional[int]
        stream_protocol: Optional[Union[str, StreamProtocol]]

        @overload
        def __init__(
                self, 
                *, 
                passphrase: Optional[str] = ..., 
                stream_id: Optional[str] = ..., 
                stream_latency: Optional[int] = ..., 
                stream_protocol: Optional[Union[str, StreamProtocol]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ForceDisabledStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTION_FORCE_DISABLED = "ConnectionForceDisabled"
        FLOW_PROFILE_FORCE_DISABLED = "FlowProfileForceDisabled"
        FLOW_TYPE_FORCE_DISABLED = "FlowTypeForceDisabled"
        PIPELINE_FORCE_DISABLED = "PipelineForceDisabled"


    class azure.mgmt.datatransfer.models.GetDestinationEndpointPortsResult(_Model):
        ports: Optional[list[int]]

        @overload
        def __init__(
                self, 
                *, 
                ports: Optional[list[int]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.GetDestinationEndpointsResult(_Model):
        endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.GetStreamConnectionStringResult(_Model):
        connection_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.IdentityTranslation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_IDENTITY = "ServiceIdentity"
        USER_IDENTITY = "UserIdentity"


    class azure.mgmt.datatransfer.models.InternalMetadataProperties(_Model):
        operation_status: Optional[OperationStatusProperties]
        status_set_by: Optional[str]


    class azure.mgmt.datatransfer.models.LinkStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINKED = "Linked"
        UNLINKED = "Unlinked"


    class azure.mgmt.datatransfer.models.ListApprovedSchemasRequest(_Model):
        direction: Optional[Union[str, Direction]]
        pipeline: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                direction: Optional[Union[str, Direction]] = ..., 
                pipeline: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ListFlowProfilesRequest(_Model):
        pipeline: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                pipeline: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ListFlowsByPipelineConnection(_Model):
        flows: Optional[list[Flow]]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                flows: Optional[list[Flow]] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ListFlowsByPipelineResult(_Model):
        value: Optional[list[ListFlowsByPipelineConnection]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[ListFlowsByPipelineConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ListParameterBody(_Model):
        connections: Optional[ConnectionIdList]

        @overload
        def __init__(
                self, 
                *, 
                connections: Optional[ConnectionIdList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ListPipelineMetadataRequest(_Model):
        pipeline: str

        @overload
        def __init__(
                self, 
                *, 
                pipeline: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ListPipelineMetadataResult(_Model):
        receive: Optional[DirectionSettings]
        send: Optional[DirectionSettings]

        @overload
        def __init__(
                self, 
                *, 
                receive: Optional[DirectionSettings] = ..., 
                send: Optional[DirectionSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.datatransfer.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.datatransfer.models.MatchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        PARTIAL = "Partial"


    class azure.mgmt.datatransfer.models.MessagingOptions(_Model):
        billing_tier: Optional[Union[str, FlowBillingTier]]
        performance_priority: Optional[Union[str, EnablementStatus]]

        @overload
        def __init__(
                self, 
                *, 
                billing_tier: Optional[Union[str, FlowBillingTier]] = ..., 
                performance_priority: Optional[Union[str, EnablementStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.MimeFilterRuleset(_Model):
        filters: Optional[list[MimeTypeFilter]]
        type: Optional[Union[str, FilterType]]

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[list[MimeTypeFilter]] = ..., 
                type: Optional[Union[str, FilterType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.MimeTypeFilter(_Model):
        extensions: Optional[list[str]]
        media: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extensions: Optional[list[str]] = ..., 
                media: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.Operation(_Model):
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


    class azure.mgmt.datatransfer.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.datatransfer.models.OperationStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.datatransfer.models.OperationStatusProperties(_Model):
        id: Optional[str]
        message: Optional[str]
        status: Optional[Union[str, OperationStatusEnum]]


    class azure.mgmt.datatransfer.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.datatransfer.models.PendingConnection(_Model):
        api_hostname: Optional[str]
        approver: Optional[str]
        date_submitted: Optional[datetime]
        direction: Optional[Union[str, Direction]]
        flow_profile_list: Optional[list[FlowProfileMetadata]]
        flow_types: Optional[list[Union[str, FlowType]]]
        force_disabled_status: Optional[list[Union[str, ForceDisabledStatus]]]
        id: Optional[str]
        justification: Optional[str]
        link_status: Optional[Union[str, LinkStatus]]
        linked_connection_id: Optional[str]
        location: str
        name: Optional[str]
        pin: Optional[str]
        pipeline: str
        policies: Optional[list[str]]
        primary_contact: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        remote_subscription_id: Optional[str]
        requirement_id: Optional[str]
        schema_uris: Optional[list[str]]
        schemas: Optional[list[Schema]]
        secondary_contacts: Optional[list[str]]
        status: Optional[Union[str, ConnectionStatus]]
        status_reason: Optional[str]
        subscription_id: Optional[str]
        system_data: Optional[SystemData]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_hostname: Optional[str] = ..., 
                direction: Optional[Union[str, Direction]] = ..., 
                flow_profile_list: Optional[list[FlowProfileMetadata]] = ..., 
                flow_types: Optional[list[Union[str, FlowType]]] = ..., 
                justification: Optional[str] = ..., 
                location: str, 
                pin: Optional[str] = ..., 
                pipeline: str, 
                policies: Optional[list[str]] = ..., 
                primary_contact: Optional[str] = ..., 
                remote_subscription_id: Optional[str] = ..., 
                requirement_id: Optional[str] = ..., 
                schema_uris: Optional[list[str]] = ..., 
                schemas: Optional[list[Schema]] = ..., 
                secondary_contacts: Optional[list[str]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.PendingFlow(_Model):
        api_flow_options: Optional[ApiFlowOptions]
        connection: Optional[SelectedResource]
        connection_id: Optional[str]
        consumer_group: Optional[str]
        customer_managed_key_vault_uri: Optional[str]
        data_type: Optional[Union[str, DataType]]
        destination_endpoint_ports: Optional[list[int]]
        destination_endpoints: Optional[list[str]]
        event_hub_id: Optional[str]
        flow_data_type: Optional[Union[str, DataClass]]
        flow_id: Optional[str]
        flow_profile: Optional[FlowProfileMetadata]
        flow_type: Optional[Union[str, FlowType]]
        force_disabled_status: Optional[list[Union[str, ForceDisabledStatus]]]
        id: Optional[str]
        key_vault_uri: Optional[str]
        link_status: Optional[Union[str, LinkStatus]]
        linked_flow_id: Optional[str]
        location: str
        messaging_options: Optional[MessagingOptions]
        name: Optional[str]
        passphrase: Optional[str]
        policies: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        schema: Optional[Schema]
        service_bus_queue_id: Optional[str]
        source_addresses: Optional[StreamSourceAddresses]
        status: Optional[Union[str, FlowStatus]]
        storage_account_id: Optional[str]
        storage_account_name: Optional[str]
        storage_container_name: Optional[str]
        storage_table_name: Optional[str]
        stream_id: Optional[str]
        stream_latency: Optional[int]
        stream_protocol: Optional[Union[str, StreamProtocol]]
        subscription_id: Optional[str]
        system_data: Optional[SystemData]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_flow_options: Optional[ApiFlowOptions] = ..., 
                connection: Optional[SelectedResource] = ..., 
                consumer_group: Optional[str] = ..., 
                customer_managed_key_vault_uri: Optional[str] = ..., 
                data_type: Optional[Union[str, DataType]] = ..., 
                destination_endpoint_ports: Optional[list[int]] = ..., 
                destination_endpoints: Optional[list[str]] = ..., 
                event_hub_id: Optional[str] = ..., 
                flow_data_type: Optional[Union[str, DataClass]] = ..., 
                flow_profile: Optional[FlowProfileMetadata] = ..., 
                flow_type: Optional[Union[str, FlowType]] = ..., 
                key_vault_uri: Optional[str] = ..., 
                location: str, 
                messaging_options: Optional[MessagingOptions] = ..., 
                passphrase: Optional[str] = ..., 
                policies: Optional[list[str]] = ..., 
                schema: Optional[Schema] = ..., 
                service_bus_queue_id: Optional[str] = ..., 
                source_addresses: Optional[StreamSourceAddresses] = ..., 
                status: Optional[Union[str, FlowStatus]] = ..., 
                storage_account_id: Optional[str] = ..., 
                storage_account_name: Optional[str] = ..., 
                storage_container_name: Optional[str] = ..., 
                storage_table_name: Optional[str] = ..., 
                stream_id: Optional[str] = ..., 
                stream_latency: Optional[int] = ..., 
                stream_protocol: Optional[Union[str, StreamProtocol]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.Pipeline(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[PipelineProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[PipelineProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.PipelineConnectionProperties(_Model):
        internal_metadata: Optional[InternalMetadataProperties]


    class azure.mgmt.datatransfer.models.PipelineProperties(_Model):
        connections: Optional[list[ReadPipelineConnection]]
        disabled_data_class: Optional[list[Union[str, DataClass]]]
        disabled_flow_types: Optional[list[Union[str, FlowType]]]
        display_name: Optional[str]
        flow_types: Optional[list[Union[str, FlowType]]]
        policies: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        quarantine_download_storage_account: Optional[str]
        quarantine_download_storage_container: Optional[str]
        remote_cloud: str
        status: Optional[Union[str, PipelineStatus]]
        subscribers: Optional[list[Subscriber]]

        @overload
        def __init__(
                self, 
                *, 
                disabled_data_class: Optional[list[Union[str, DataClass]]] = ..., 
                disabled_flow_types: Optional[list[Union[str, FlowType]]] = ..., 
                display_name: Optional[str] = ..., 
                flow_types: Optional[list[Union[str, FlowType]]] = ..., 
                policies: Optional[list[str]] = ..., 
                quarantine_download_storage_account: Optional[str] = ..., 
                quarantine_download_storage_container: Optional[str] = ..., 
                remote_cloud: str, 
                status: Optional[Union[str, PipelineStatus]] = ..., 
                subscribers: Optional[list[Subscriber]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.PipelineStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.datatransfer.models.PipelinesPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[PipelinesPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[PipelinesPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.PipelinesPatchProperties(_Model):
        flow_types: Optional[list[Union[str, FlowType]]]

        @overload
        def __init__(
                self, 
                *, 
                flow_types: Optional[list[Union[str, FlowType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.Plan(_Model):
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


    class azure.mgmt.datatransfer.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.datatransfer.models.ReadPipelineConnection(_Model):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: Optional[str]
        properties: Optional[PipelineConnectionProperties]
        system_data: Optional[SystemData]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                id: str, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[PipelineConnectionProperties] = ..., 
                system_data: Optional[SystemData] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.RemoteEndpointSettings(_Model):
        authentication: Optional[list[Authentication]]
        endpoint: str

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[list[Authentication]] = ..., 
                endpoint: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.datatransfer.models.ResourceBody(_Model):
        id: str
        status_reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                status_reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.Schema(_Model):
        connection_id: Optional[str]
        content: Optional[str]
        direction: Optional[Union[str, Direction]]
        id: Optional[str]
        name: Optional[str]
        schema_type: Optional[Union[str, SchemaType]]
        schema_uri: Optional[str]
        status: Optional[Union[str, SchemaStatus]]

        @overload
        def __init__(
                self, 
                *, 
                connection_id: Optional[str] = ..., 
                content: Optional[str] = ..., 
                direction: Optional[Union[str, Direction]] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                schema_type: Optional[Union[str, SchemaType]] = ..., 
                schema_uri: Optional[str] = ..., 
                status: Optional[Union[str, SchemaStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.SchemaStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        NEW = "New"


    class azure.mgmt.datatransfer.models.SchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        XSD = "Xsd"
        ZIP = "Zip"


    class azure.mgmt.datatransfer.models.SchemasListResult(_Model):
        value: Optional[list[Schema]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[Schema]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.SelectedResource(_Model):
        id: str
        location: Optional[str]
        name: Optional[str]
        subscription_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                subscription_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.SetDestinationEndpointPorts(_Model):
        ports: Optional[list[int]]

        @overload
        def __init__(
                self, 
                *, 
                ports: Optional[list[int]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.SetDestinationEndpoints(_Model):
        endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.SetSourceAddresses(_Model):
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.SetStreamPassphrase(_Model):
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.StreamProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RTP = "RTP"
        SRT = "SRT"
        UDP = "UDP"


    class azure.mgmt.datatransfer.models.StreamSourceAddresses(_Model):
        source_addresses: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                source_addresses: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.Subscriber(_Model):
        email: Optional[str]
        notifications: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                email: Optional[str] = ..., 
                notifications: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.SystemData(_Model):
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


    class azure.mgmt.datatransfer.models.TargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTION = "Connection"
        FLOW_PROFILE = "FlowProfile"
        FLOW_TYPE = "FlowType"
        PIPELINE = "Pipeline"


    class azure.mgmt.datatransfer.models.TextMatchingRuleset(_Model):
        deny: Optional[list[TextMatchingRulesetDeny]]

        @overload
        def __init__(
                self, 
                *, 
                deny: Optional[list[TextMatchingRulesetDeny]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.TextMatchingRulesetDeny(_Model):
        case_sensitivity: Union[str, Casing]
        match_type: Union[str, MatchType]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                case_sensitivity: Union[str, Casing], 
                match_type: Union[str, MatchType], 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.TrackedResource(Resource):
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


    class azure.mgmt.datatransfer.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.datatransfer.models.ValidateSchemaResult(_Model):
        message: Optional[str]
        status: Optional[Union[str, ValidateSchemaStatus]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status: Optional[Union[str, ValidateSchemaStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.ValidateSchemaStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.datatransfer.models.XmlFilterRuleset(_Model):
        default_namespace: Optional[str]
        reference: Optional[Union[str, XmlReferenceType]]
        schema: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_namespace: Optional[str] = ..., 
                reference: Optional[Union[str, XmlReferenceType]] = ..., 
                schema: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.datatransfer.models.XmlReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "Inline"


namespace azure.mgmt.datatransfer.operations

    class azure.mgmt.datatransfer.operations.AzureDataTransferOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def list_approved_schemas(
                self, 
                pipeline: ListApprovedSchemasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        def list_approved_schemas(
                self, 
                pipeline: ListApprovedSchemasRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        def list_approved_schemas(
                self, 
                pipeline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        def list_flow_profiles(
                self, 
                body: ListFlowProfilesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FlowProfilesListResult: ...

        @overload
        def list_flow_profiles(
                self, 
                body: ListFlowProfilesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FlowProfilesListResult: ...

        @overload
        def list_flow_profiles(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FlowProfilesListResult: ...

        @overload
        def list_pipeline_metadata(
                self, 
                body: ListPipelineMetadataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListPipelineMetadataResult: ...

        @overload
        def list_pipeline_metadata(
                self, 
                body: ListPipelineMetadataRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListPipelineMetadataResult: ...

        @overload
        def list_pipeline_metadata(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListPipelineMetadataResult: ...

        @overload
        def validate_schema(
                self, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSchemaResult: ...

        @overload
        def validate_schema(
                self, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSchemaResult: ...

        @overload
        def validate_schema(
                self, 
                schema: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSchemaResult: ...


    class azure.mgmt.datatransfer.operations.ConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: Connection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ConnectionsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: ConnectionsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PendingConnection]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Connection]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Connection]: ...

        @distributed_trace
        def list_pending_flows_list(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PendingFlow]: ...


    class azure.mgmt.datatransfer.operations.FlowProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                resource: FlowProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FlowProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                resource: FlowProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FlowProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FlowProfile]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-30-preview', params_added_on={'2025-05-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'pipeline_name', 'flow_profile_name']}, api_versions_list=['2025-05-30-preview', '2025-10-10-preview', '2026-02-06-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                properties: FlowProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FlowProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                properties: FlowProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FlowProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FlowProfile]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-30-preview', params_added_on={'2025-05-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'pipeline_name', 'flow_profile_name', 'accept']}, api_versions_list=['2025-05-30-preview', '2025-10-10-preview', '2026-02-06-preview'])
        def get(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                flow_profile_name: str, 
                **kwargs: Any
            ) -> FlowProfile: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-05-30-preview', params_added_on={'2025-05-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'pipeline_name', 'accept']}, api_versions_list=['2025-05-30-preview', '2025-10-10-preview', '2026-02-06-preview'])
        def list_by_pipeline(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FlowProfile]: ...


    class azure.mgmt.datatransfer.operations.FlowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: Flow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: Flow, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_disable(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @distributed_trace
        def begin_enable(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @distributed_trace
        def begin_generate_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_link(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoint_ports: SetDestinationEndpointPorts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoint_ports: SetDestinationEndpointPorts, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoint_ports: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoints: SetDestinationEndpoints, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoints: SetDestinationEndpoints, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                stream_destination_endpoints: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                passphrase: SetStreamPassphrase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                passphrase: SetStreamPassphrase, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_passphrase(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                passphrase: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                source_addresses: SetSourceAddresses, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                source_addresses: SetSourceAddresses, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_set_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                source_addresses: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Flow]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: FlowsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: FlowsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                flow: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> Flow: ...

        @distributed_trace
        def get_destination_endpoint_ports(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> GetDestinationEndpointPortsResult: ...

        @distributed_trace
        def get_destination_endpoints(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> GetDestinationEndpointsResult: ...

        @distributed_trace
        def get_source_addresses(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> StreamSourceAddresses: ...

        @distributed_trace
        def get_stream_connection_string(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                flow_name: str, 
                **kwargs: Any
            ) -> GetStreamConnectionStringResult: ...

        @distributed_trace
        def list_by_connection(
                self, 
                resource_group_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Flow]: ...


    class azure.mgmt.datatransfer.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.datatransfer.operations.PipelinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_approve_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_approve_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_approve_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: Pipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pipeline]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: Pipeline, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pipeline]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pipeline]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute_action(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                action: Action, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pipeline]: ...

        @overload
        def begin_execute_action(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                action: Action, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pipeline]: ...

        @overload
        def begin_execute_action(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                action: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pipeline]: ...

        @overload
        def begin_reject_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_reject_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: ResourceBody, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_reject_connection(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Connection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: PipelinesPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: PipelinesPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                pipeline: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                **kwargs: Any
            ) -> Pipeline: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connections: Optional[ConnectionIdList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListFlowsByPipelineResult: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connections: Optional[ConnectionIdList] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListFlowsByPipelineResult: ...

        @overload
        def list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                connections: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ListFlowsByPipelineResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Pipeline]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Pipeline]: ...

        @overload
        def list_schemas_list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        def list_schemas_list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                schema: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...

        @overload
        def list_schemas_list(
                self, 
                resource_group_name: str, 
                pipeline_name: str, 
                schema: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemasListResult: ...


namespace azure.mgmt.datatransfer.types

    class azure.mgmt.datatransfer.types.Action(TypedDict, total=False):
        key "actionType": Required[Union[str, DateTransferActionType]]
        key "justification": str
        key "targetType": Required[Union[str, TargetType]]
        actionType: Union[str, DateTransferActionType]
        justification: str
        targetType: Union[str, TargetType]
        targets: list[str]


    class azure.mgmt.datatransfer.types.AntivirusRuleset(TypedDict, total=False):
        avSolutions: list[Union[str, AntivirusSolutions]]


    class azure.mgmt.datatransfer.types.ApiFlowOptions(TypedDict, total=False):
        key "apiMode": Union[str, ApiMode]
        key "audienceOverride": str
        key "cname": str
        key "identityTranslation": Union[str, IdentityTranslation]
        key "remoteCallingModeClientId": str
        key "remoteEndpoint": str
        key "remoteEndpointSettings": ForwardRef('RemoteEndpointSettings', module='types')
        key "senderClientId": str
        apiMode: Union[str, ApiMode]
        audienceOverride: str
        authentication: list[Authentication]
        cname: str
        identityTranslation: Union[str, IdentityTranslation]
        remoteCallingModeClientId: str
        remoteEndpoint: str
        remoteEndpointSettings: RemoteEndpointSettings
        senderClientId: str


    class azure.mgmt.datatransfer.types.ArchiveRuleset(TypedDict, total=False):
        key "maximumCompressionRatioLimit": float
        key "maximumDepthLimit": int
        key "maximumExpansionSizeLimit": int
        key "minimumSizeForExpansion": int
        maximumCompressionRatioLimit: float
        maximumDepthLimit: int
        maximumExpansionSizeLimit: int
        minimumSizeForExpansion: int


    class azure.mgmt.datatransfer.types.Authentication(TypedDict, total=False):
        key "audience": str
        key "authority": str
        key "clientIdOverride": str
        key "identityTranslation": Union[str, IdentityTranslation]
        key "instance": str
        key "tenantId": str
        key "type": Union[str, AuthenticationType]
        applicationIds: list[str]
        audience: str
        authority: str
        clientIdOverride: str
        identityTranslation: Union[str, IdentityTranslation]
        instance: str
        tenantId: str
        type: Union[str, AuthenticationType]


    class azure.mgmt.datatransfer.types.Connection(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ConnectionProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.datatransfer.types.ConnectionIdList(TypedDict, total=False):
        value: list[str]


    class azure.mgmt.datatransfer.types.ConnectionProperties(TypedDict, total=False):
        key "apiHostname": str
        key "approver": str
        key "dateSubmitted": str
        key "direction": Union[str, Direction]
        key "justification": str
        key "linkStatus": Union[str, LinkStatus]
        key "linkedConnectionId": str
        key "pin": str
        key "pipeline": Required[str]
        key "primaryContact": str
        key "provisioningState": Union[str, ProvisioningState]
        key "remoteSubscriptionId": str
        key "requirementId": str
        key "status": Union[str, ConnectionStatus]
        key "statusReason": str
        apiHostname: str
        approver: str
        dateSubmitted: str
        direction: Union[str, Direction]
        flowProfileList: list[FlowProfileMetadata]
        flowTypes: list[Union[str, FlowType]]
        forceDisabledStatus: list[Union[str, ForceDisabledStatus]]
        justification: str
        linkStatus: Union[str, LinkStatus]
        linkedConnectionId: str
        pin: str
        pipeline: str
        policies: list[str]
        primaryContact: str
        provisioningState: Union[str, ProvisioningState]
        remoteSubscriptionId: str
        requirementId: str
        schemaUris: list[str]
        schemas: list[Schema]
        secondaryContacts: list[str]
        status: Union[str, ConnectionStatus]
        statusReason: str


    class azure.mgmt.datatransfer.types.ConnectionsPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.datatransfer.types.DataSizeRuleset(TypedDict, total=False):
        key "maximum": int
        key "minimum": int
        maximum: int
        minimum: int


    class azure.mgmt.datatransfer.types.Flow(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "plan": ForwardRef('Plan', module='types')
        key "properties": ForwardRef('FlowProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        plan: Plan
        properties: FlowProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.datatransfer.types.FlowProfile(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('FlowProfileProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: FlowProfileProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.datatransfer.types.FlowProfileMetadata(TypedDict, total=False):
        key "description": Required[str]
        key "flowProfileId": Required[str]
        key "name": Required[str]
        key "pipeline": Required[str]
        key "replicationScenario": Required[Union[str, DataClassType]]
        key "status": Required[Union[str, FlowProfileStatus]]
        description: str
        flowProfileId: str
        name: str
        pipeline: str
        replicationScenario: Union[str, DataClassType]
        status: Union[str, FlowProfileStatus]


    class azure.mgmt.datatransfer.types.FlowProfilePatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('FlowProfilePatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: FlowProfilePatchProperties
        tags: dict[str, str]


    class azure.mgmt.datatransfer.types.FlowProfilePatchProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, ProvisioningState]
        key "rulesets": ForwardRef('FlowProfileRulesets', module='types')
        key "status": Union[str, FlowProfileStatus]
        description: str
        provisioningState: Union[str, ProvisioningState]
        rulesets: FlowProfileRulesets
        status: Union[str, FlowProfileStatus]


    class azure.mgmt.datatransfer.types.FlowProfileProperties(TypedDict, total=False):
        key "description": Required[str]
        key "flowProfileId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "replicationScenario": Required[Union[str, DataClassType]]
        key "rulesets": ForwardRef('FlowProfileRulesets', module='types')
        key "status": Required[Union[str, FlowProfileStatus]]
        description: str
        flowProfileId: str
        provisioningState: Union[str, ProvisioningState]
        replicationScenario: Union[str, DataClassType]
        rulesets: FlowProfileRulesets
        status: Union[str, FlowProfileStatus]


    class azure.mgmt.datatransfer.types.FlowProfileRulesets(TypedDict, total=False):
        key "antivirus": ForwardRef('AntivirusRuleset', module='types')
        key "archives": ForwardRef('ArchiveRuleset', module='types')
        key "dataSize": ForwardRef('DataSizeRuleset', module='types')
        key "mimeFilters": ForwardRef('MimeFilterRuleset', module='types')
        key "textMatching": ForwardRef('TextMatchingRuleset', module='types')
        key "xmlFilters": ForwardRef('XmlFilterRuleset', module='types')
        antivirus: AntivirusRuleset
        archives: ArchiveRuleset
        dataSize: DataSizeRuleset
        mimeFilters: MimeFilterRuleset
        textMatching: TextMatchingRuleset
        xmlFilters: XmlFilterRuleset


    class azure.mgmt.datatransfer.types.FlowProperties(TypedDict, total=False):
        key "apiFlowOptions": ForwardRef('ApiFlowOptions', module='types')
        key "connection": ForwardRef('SelectedResource', module='types')
        key "consumerGroup": str
        key "customerManagedKeyVaultUri": str
        key "dataType": Union[str, DataType]
        key "eventHubId": str
        key "flowDataType": Union[str, DataClass]
        key "flowId": str
        key "flowProfile": ForwardRef('FlowProfileMetadata', module='types')
        key "flowType": Union[str, FlowType]
        key "keyVaultUri": str
        key "linkStatus": Union[str, LinkStatus]
        key "linkedFlowId": str
        key "messagingOptions": ForwardRef('MessagingOptions', module='types')
        key "passphrase": str
        key "provisioningState": Union[str, ProvisioningState]
        key "schema": ForwardRef('Schema', module='types')
        key "serviceBusQueueId": str
        key "sourceAddresses": ForwardRef('StreamSourceAddresses', module='types')
        key "status": Union[str, FlowStatus]
        key "storageAccountId": str
        key "storageAccountName": str
        key "storageContainerName": str
        key "storageTableName": str
        key "streamId": str
        key "streamLatency": int
        key "streamProtocol": Union[str, StreamProtocol]
        apiFlowOptions: ApiFlowOptions
        connection: SelectedResource
        consumerGroup: str
        customerManagedKeyVaultUri: str
        dataType: Union[str, DataType]
        destinationEndpointPorts: list[int]
        destinationEndpoints: list[str]
        eventHubId: str
        flowDataType: Union[str, DataClass]
        flowId: str
        flowProfile: FlowProfileMetadata
        flowType: Union[str, FlowType]
        forceDisabledStatus: list[Union[str, ForceDisabledStatus]]
        keyVaultUri: str
        linkStatus: Union[str, LinkStatus]
        linkedFlowId: str
        messagingOptions: MessagingOptions
        passphrase: str
        policies: list[str]
        provisioningState: Union[str, ProvisioningState]
        schema: Schema
        serviceBusQueueId: str
        sourceAddresses: StreamSourceAddresses
        status: Union[str, FlowStatus]
        storageAccountId: str
        storageAccountName: str
        storageContainerName: str
        storageTableName: str
        streamId: str
        streamLatency: int
        streamProtocol: Union[str, StreamProtocol]


    class azure.mgmt.datatransfer.types.FlowsPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('FlowsPatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: FlowsPatchProperties
        tags: dict[str, str]


    class azure.mgmt.datatransfer.types.FlowsPatchProperties(TypedDict, total=False):
        key "passphrase": str
        key "streamId": str
        key "streamLatency": int
        key "streamProtocol": Union[str, StreamProtocol]
        passphrase: str
        streamId: str
        streamLatency: int
        streamProtocol: Union[str, StreamProtocol]


    class azure.mgmt.datatransfer.types.InternalMetadataProperties(TypedDict, total=False):
        key "operationStatus": ForwardRef('OperationStatusProperties', module='types')
        key "statusSetBy": str
        operationStatus: OperationStatusProperties
        statusSetBy: str


    class azure.mgmt.datatransfer.types.ListApprovedSchemasRequest(TypedDict, total=False):
        key "direction": Union[str, Direction]
        key "pipeline": str
        direction: Union[str, Direction]
        pipeline: str


    class azure.mgmt.datatransfer.types.ListFlowProfilesRequest(TypedDict, total=False):
        key "pipeline": str
        pipeline: str


    class azure.mgmt.datatransfer.types.ListPipelineMetadataRequest(TypedDict, total=False):
        key "pipeline": Required[str]
        pipeline: str


    class azure.mgmt.datatransfer.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.datatransfer.types.MessagingOptions(TypedDict, total=False):
        key "billingTier": Union[str, FlowBillingTier]
        key "performancePriority": Union[str, EnablementStatus]
        billingTier: Union[str, FlowBillingTier]
        performancePriority: Union[str, EnablementStatus]


    class azure.mgmt.datatransfer.types.MimeFilterRuleset(TypedDict, total=False):
        key "type": Union[str, FilterType]
        filters: list[MimeTypeFilter]
        type: Union[str, FilterType]


    class azure.mgmt.datatransfer.types.MimeTypeFilter(TypedDict, total=False):
        key "media": str
        extensions: list[str]
        media: str


    class azure.mgmt.datatransfer.types.OperationStatusProperties(TypedDict, total=False):
        key "id": str
        key "message": str
        key "status": Union[str, OperationStatusEnum]
        id: str
        message: str
        status: Union[str, OperationStatusEnum]


    class azure.mgmt.datatransfer.types.Pipeline(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PipelineProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: PipelineProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.datatransfer.types.PipelineConnectionProperties(TypedDict, total=False):
        key "internalMetadata": ForwardRef('InternalMetadataProperties', module='types')
        internalMetadata: InternalMetadataProperties


    class azure.mgmt.datatransfer.types.PipelineProperties(TypedDict, total=False):
        key "displayName": str
        key "provisioningState": Union[str, ProvisioningState]
        key "quarantineDownloadStorageAccount": str
        key "quarantineDownloadStorageContainer": str
        key "remoteCloud": Required[str]
        key "status": Union[str, PipelineStatus]
        connections: list[ReadPipelineConnection]
        disabledDataClass: list[Union[str, DataClass]]
        disabledFlowTypes: list[Union[str, FlowType]]
        displayName: str
        flowTypes: list[Union[str, FlowType]]
        policies: list[str]
        provisioningState: Union[str, ProvisioningState]
        quarantineDownloadStorageAccount: str
        quarantineDownloadStorageContainer: str
        remoteCloud: str
        status: Union[str, PipelineStatus]
        subscribers: list[Subscriber]


    class azure.mgmt.datatransfer.types.PipelinesPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('PipelinesPatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: PipelinesPatchProperties
        tags: dict[str, str]


    class azure.mgmt.datatransfer.types.PipelinesPatchProperties(TypedDict, total=False):
        flowTypes: list[Union[str, FlowType]]


    class azure.mgmt.datatransfer.types.Plan(TypedDict, total=False):
        key "name": Required[str]
        key "product": Required[str]
        key "promotionCode": str
        key "publisher": Required[str]
        key "version": str
        name: str
        product: str
        promotionCode: str
        publisher: str
        version: str


    class azure.mgmt.datatransfer.types.ReadPipelineConnection(TypedDict, total=False):
        key "etag": str
        key "id": Required[str]
        key "location": str
        key "name": str
        key "properties": ForwardRef('PipelineConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: PipelineConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.datatransfer.types.RemoteEndpointSettings(TypedDict, total=False):
        key "endpoint": Required[str]
        authentication: list[Authentication]
        endpoint: str


    class azure.mgmt.datatransfer.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.datatransfer.types.ResourceBody(TypedDict, total=False):
        key "id": Required[str]
        key "statusReason": str
        id: str
        statusReason: str


    class azure.mgmt.datatransfer.types.Schema(TypedDict, total=False):
        key "connectionId": str
        key "content": str
        key "direction": Union[str, Direction]
        key "id": str
        key "name": str
        key "schemaType": Union[str, SchemaType]
        key "schemaUri": str
        key "status": Union[str, SchemaStatus]
        connectionId: str
        content: str
        direction: Union[str, Direction]
        id: str
        name: str
        schemaType: Union[str, SchemaType]
        schemaUri: str
        status: Union[str, SchemaStatus]


    class azure.mgmt.datatransfer.types.SelectedResource(TypedDict, total=False):
        key "id": Required[str]
        key "location": str
        key "name": str
        key "subscriptionName": str
        id: str
        location: str
        name: str
        subscriptionName: str


    class azure.mgmt.datatransfer.types.SetDestinationEndpointPorts(TypedDict, total=False):
        ports: list[int]


    class azure.mgmt.datatransfer.types.SetDestinationEndpoints(TypedDict, total=False):
        endpoints: list[str]


    class azure.mgmt.datatransfer.types.SetSourceAddresses(TypedDict, total=False):
        values: list[str]


    class azure.mgmt.datatransfer.types.SetStreamPassphrase(TypedDict, total=False):
        key "value": str
        value: str


    class azure.mgmt.datatransfer.types.StreamSourceAddresses(TypedDict, total=False):
        sourceAddresses: list[str]


    class azure.mgmt.datatransfer.types.Subscriber(TypedDict, total=False):
        key "email": str
        key "notifications": int
        email: str
        notifications: int


    class azure.mgmt.datatransfer.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.datatransfer.types.TextMatchingRuleset(TypedDict, total=False):
        deny: list[TextMatchingRulesetDeny]


    class azure.mgmt.datatransfer.types.TextMatchingRulesetDeny(TypedDict, total=False):
        key "caseSensitivity": Required[Union[str, Casing]]
        key "matchType": Required[Union[str, MatchType]]
        key "text": Required[str]
        caseSensitivity: Union[str, Casing]
        matchType: Union[str, MatchType]
        text: str


    class azure.mgmt.datatransfer.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.datatransfer.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.datatransfer.types.XmlFilterRuleset(TypedDict, total=False):
        key "defaultNamespace": str
        key "reference": Union[str, XmlReferenceType]
        key "schema": str
        defaultNamespace: str
        reference: Union[str, XmlReferenceType]
        schema: str


```