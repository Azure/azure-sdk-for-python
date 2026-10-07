```py
namespace azure.mgmt.iotoperations

    class azure.mgmt.iotoperations.IoTOperationsMgmtClient: implements ContextManager 
        akri_connector: AkriConnectorOperations
        akri_connector_template: AkriConnectorTemplateOperations
        akri_service: AkriServiceOperations
        broker: BrokerOperations
        broker_authentication: BrokerAuthenticationOperations
        broker_authorization: BrokerAuthorizationOperations
        broker_listener: BrokerListenerOperations
        dataflow: DataflowOperations
        dataflow_endpoint: DataflowEndpointOperations
        dataflow_graph: DataflowGraphOperations
        dataflow_profile: DataflowProfileOperations
        instance: InstanceOperations
        operations: Operations
        registry_endpoint: RegistryEndpointOperations

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


namespace azure.mgmt.iotoperations.aio

    class azure.mgmt.iotoperations.aio.IoTOperationsMgmtClient: implements AsyncContextManager 
        akri_connector: AkriConnectorOperations
        akri_connector_template: AkriConnectorTemplateOperations
        akri_service: AkriServiceOperations
        broker: BrokerOperations
        broker_authentication: BrokerAuthenticationOperations
        broker_authorization: BrokerAuthorizationOperations
        broker_listener: BrokerListenerOperations
        dataflow: DataflowOperations
        dataflow_endpoint: DataflowEndpointOperations
        dataflow_graph: DataflowGraphOperations
        dataflow_profile: DataflowProfileOperations
        instance: InstanceOperations
        operations: Operations
        registry_endpoint: RegistryEndpointOperations

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


namespace azure.mgmt.iotoperations.aio.operations

    class azure.mgmt.iotoperations.aio.operations.AkriConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                resource: AkriConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriConnectorResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                resource: AkriConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriConnectorResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriConnectorResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AkriConnectorResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_template(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AkriConnectorResource]: ...


    class azure.mgmt.iotoperations.aio.operations.AkriConnectorTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                resource: AkriConnectorTemplateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriConnectorTemplateResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                resource: AkriConnectorTemplateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriConnectorTemplateResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriConnectorTemplateResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> AkriConnectorTemplateResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_instance_resource(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AkriConnectorTemplateResource]: ...


    class azure.mgmt.iotoperations.aio.operations.AkriServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                resource: AkriServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                resource: AkriServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AkriServiceResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name']}, api_versions_list=['2026-03-01', '2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name', 'accept']}, api_versions_list=['2026-03-01', '2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> AkriServiceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2026-03-01', '2026-07-01'])
        def list_by_instance_resource(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AkriServiceResource]: ...


    class azure.mgmt.iotoperations.aio.operations.BrokerAuthenticationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                resource: BrokerAuthenticationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerAuthenticationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                resource: BrokerAuthenticationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerAuthenticationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerAuthenticationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                **kwargs: Any
            ) -> BrokerAuthenticationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BrokerAuthenticationResource]: ...


    class azure.mgmt.iotoperations.aio.operations.BrokerAuthorizationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                resource: BrokerAuthorizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerAuthorizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                resource: BrokerAuthorizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerAuthorizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerAuthorizationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> BrokerAuthorizationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BrokerAuthorizationResource]: ...


    class azure.mgmt.iotoperations.aio.operations.BrokerListenerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                resource: BrokerListenerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerListenerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                resource: BrokerListenerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerListenerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerListenerResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                **kwargs: Any
            ) -> BrokerListenerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BrokerListenerResource]: ...


    class azure.mgmt.iotoperations.aio.operations.BrokerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                resource: BrokerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                resource: BrokerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BrokerResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> BrokerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BrokerResource]: ...


    class azure.mgmt.iotoperations.aio.operations.DataflowEndpointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                resource: DataflowEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                resource: DataflowEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowEndpointResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                **kwargs: Any
            ) -> DataflowEndpointResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataflowEndpointResource]: ...


    class azure.mgmt.iotoperations.aio.operations.DataflowGraphOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                resource: DataflowGraphResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowGraphResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                resource: DataflowGraphResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowGraphResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowGraphResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> DataflowGraphResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_dataflow_profile(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataflowGraphResource]: ...


    class azure.mgmt.iotoperations.aio.operations.DataflowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                resource: DataflowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                resource: DataflowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                **kwargs: Any
            ) -> DataflowResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataflowResource]: ...


    class azure.mgmt.iotoperations.aio.operations.DataflowProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                resource: DataflowProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowProfileResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                resource: DataflowProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowProfileResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataflowProfileResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> DataflowProfileResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataflowProfileResource]: ...


    class azure.mgmt.iotoperations.aio.operations.InstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                resource: InstanceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InstanceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                resource: InstanceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InstanceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InstanceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> InstanceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InstanceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[InstanceResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                properties: InstancePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InstanceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                properties: InstancePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InstanceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InstanceResource: ...


    class azure.mgmt.iotoperations.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.iotoperations.aio.operations.RegistryEndpointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                resource: RegistryEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                resource: RegistryEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryEndpointResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryEndpointResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> RegistryEndpointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_instance_resource(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RegistryEndpointResource]: ...


namespace azure.mgmt.iotoperations.models

    class azure.mgmt.iotoperations.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.iotoperations.models.AdvancedSettings(_Model):
        clients: Optional[ClientConfig]
        encrypt_internal_traffic: Optional[Union[str, OperationalMode]]
        internal_certs: Optional[CertManagerCertOptions]

        @overload
        def __init__(
                self, 
                *, 
                clients: Optional[ClientConfig] = ..., 
                encrypt_internal_traffic: Optional[Union[str, OperationalMode]] = ..., 
                internal_certs: Optional[CertManagerCertOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorAllocatedDevice(_Model):
        device_inbound_endpoint_name: str
        device_name: str


    class azure.mgmt.iotoperations.models.AkriConnectorProperties(_Model):
        allocated_devices: Optional[list[AkriConnectorAllocatedDevice]]
        health_state: Optional[Union[str, ResourceHealthState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[AkriConnectorStatus]


    class azure.mgmt.iotoperations.models.AkriConnectorResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[AkriConnectorProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[AkriConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorStatus(_Model):
        health_state: Optional[ResourceHealthStatus]


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateAioMetadata(_Model):
        aio_max_version: Optional[str]
        aio_min_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aio_max_version: Optional[str] = ..., 
                aio_min_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateAllocation(_Model):
        policy: str

        @overload
        def __init__(
                self, 
                *, 
                policy: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateAllocationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUCKETIZED = "Bucketized"


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateBucketizedAllocation(AkriConnectorTemplateAllocation, discriminator='Bucketized'):
        bucket_size: int
        policy: Literal[AkriConnectorTemplateAllocationPolicy.BUCKETIZED]

        @overload
        def __init__(
                self, 
                *, 
                bucket_size: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateDeviceInboundEndpointType(_Model):
        display_name: Optional[str]
        endpoint_type: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                endpoint_type: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateDiagnostics(_Model):
        logs: AkriConnectorsDiagnosticsLogs

        @overload
        def __init__(
                self, 
                *, 
                logs: AkriConnectorsDiagnosticsLogs
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateExecAction(_Model):
        command: list[str]

        @overload
        def __init__(
                self, 
                *, 
                command: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateManagedConfiguration(AkriConnectorTemplateRuntimeConfiguration, discriminator='ManagedConfiguration'):
        managed_configuration_settings: AkriConnectorTemplateManagedConfigurationSettings
        runtime_configuration_type: Literal[AkriConnectorTemplateRuntimeConfigurationType.MANAGED_CONFIGURATION]

        @overload
        def __init__(
                self, 
                *, 
                managed_configuration_settings: AkriConnectorTemplateManagedConfigurationSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateManagedConfigurationSettings(_Model):
        additional_configuration: Optional[dict[str, str]]
        allocation: Optional[AkriConnectorTemplateAllocation]
        managed_configuration_type: str
        persistent_volume_claim_templates: Optional[list[dict[str, Any]]]
        persistent_volume_claims: Optional[list[AkriConnectorTemplatePersistentVolumeClaim]]
        secrets: Optional[list[AkriConnectorsSecret]]
        trust_settings: Optional[AkriConnectorTemplateTrustList]

        @overload
        def __init__(
                self, 
                *, 
                additional_configuration: Optional[dict[str, str]] = ..., 
                allocation: Optional[AkriConnectorTemplateAllocation] = ..., 
                managed_configuration_type: str, 
                persistent_volume_claim_templates: Optional[list[dict[str, Any]]] = ..., 
                persistent_volume_claims: Optional[list[AkriConnectorTemplatePersistentVolumeClaim]] = ..., 
                secrets: Optional[list[AkriConnectorsSecret]] = ..., 
                trust_settings: Optional[AkriConnectorTemplateTrustList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateManagedConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE_CONFIGURATION = "ImageConfiguration"
        STATEFUL_SET_CONFIGURATION = "StatefulSetConfiguration"


    class azure.mgmt.iotoperations.models.AkriConnectorTemplatePersistentVolumeClaim(_Model):
        claim_name: str
        mount_path: str

        @overload
        def __init__(
                self, 
                *, 
                claim_name: str, 
                mount_path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateProperties(_Model):
        aio_metadata: Optional[AkriConnectorTemplateAioMetadata]
        connector_metadata_ref: Optional[str]
        device_inbound_endpoint_types: list[AkriConnectorTemplateDeviceInboundEndpointType]
        diagnostics: Optional[AkriConnectorTemplateDiagnostics]
        health_state: Optional[Union[str, ResourceHealthState]]
        mqtt_connection_configuration: Optional[AkriConnectorsMqttConnectionConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        runtime_configuration: AkriConnectorTemplateRuntimeConfiguration

        @overload
        def __init__(
                self, 
                *, 
                aio_metadata: Optional[AkriConnectorTemplateAioMetadata] = ..., 
                connector_metadata_ref: Optional[str] = ..., 
                device_inbound_endpoint_types: list[AkriConnectorTemplateDeviceInboundEndpointType], 
                diagnostics: Optional[AkriConnectorTemplateDiagnostics] = ..., 
                mqtt_connection_configuration: Optional[AkriConnectorsMqttConnectionConfiguration] = ..., 
                runtime_configuration: AkriConnectorTemplateRuntimeConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateReadinessProbe(_Model):
        exec_property: Optional[AkriConnectorTemplateExecAction]
        failure_threshold: Optional[int]
        initial_delay_seconds: Optional[int]
        period_seconds: Optional[int]
        success_threshold: Optional[int]
        timeout_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                exec_property: Optional[AkriConnectorTemplateExecAction] = ..., 
                failure_threshold: Optional[int] = ..., 
                initial_delay_seconds: Optional[int] = ..., 
                period_seconds: Optional[int] = ..., 
                success_threshold: Optional[int] = ..., 
                timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[AkriConnectorTemplateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[AkriConnectorTemplateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateRuntimeConfiguration(_Model):
        runtime_configuration_type: str

        @overload
        def __init__(
                self, 
                *, 
                runtime_configuration_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateRuntimeConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_CONFIGURATION = "ManagedConfiguration"


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateRuntimeImageConfiguration(AkriConnectorTemplateManagedConfigurationSettings, discriminator='ImageConfiguration'):
        additional_configuration: dict[str, str]
        allocation: AkriConnectorTemplateAllocation
        image_configuration_settings: AkriConnectorTemplateRuntimeImageConfigurationSettings
        managed_configuration_type: Literal[AkriConnectorTemplateManagedConfigurationType.IMAGE_CONFIGURATION]
        persistent_volume_claim_templates: list[dict[str, any]]
        persistent_volume_claims: list[AkriConnectorTemplatePersistentVolumeClaim]
        secrets: list[AkriConnectorsSecret]
        trust_settings: AkriConnectorTemplateTrustList

        @overload
        def __init__(
                self, 
                *, 
                additional_configuration: Optional[dict[str, str]] = ..., 
                allocation: Optional[AkriConnectorTemplateAllocation] = ..., 
                image_configuration_settings: AkriConnectorTemplateRuntimeImageConfigurationSettings, 
                persistent_volume_claim_templates: Optional[list[dict[str, Any]]] = ..., 
                persistent_volume_claims: Optional[list[AkriConnectorTemplatePersistentVolumeClaim]] = ..., 
                secrets: Optional[list[AkriConnectorsSecret]] = ..., 
                trust_settings: Optional[AkriConnectorTemplateTrustList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateRuntimeImageConfigurationSettings(_Model):
        image_name: str
        image_pull_policy: Optional[Union[str, AkriConnectorsImagePullPolicy]]
        readiness_probe: Optional[AkriConnectorTemplateReadinessProbe]
        registry_settings: Optional[AkriConnectorsRegistrySettings]
        replicas: Optional[int]
        tag_digest_settings: Optional[AkriConnectorsTagDigestSettings]

        @overload
        def __init__(
                self, 
                *, 
                image_name: str, 
                image_pull_policy: Optional[Union[str, AkriConnectorsImagePullPolicy]] = ..., 
                readiness_probe: Optional[AkriConnectorTemplateReadinessProbe] = ..., 
                registry_settings: Optional[AkriConnectorsRegistrySettings] = ..., 
                replicas: Optional[int] = ..., 
                tag_digest_settings: Optional[AkriConnectorsTagDigestSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateRuntimeStatefulSetConfiguration(AkriConnectorTemplateManagedConfigurationSettings, discriminator='StatefulSetConfiguration'):
        additional_configuration: dict[str, str]
        allocation: AkriConnectorTemplateAllocation
        managed_configuration_type: Literal[AkriConnectorTemplateManagedConfigurationType.STATEFUL_SET_CONFIGURATION]
        persistent_volume_claim_templates: list[dict[str, any]]
        persistent_volume_claims: list[AkriConnectorTemplatePersistentVolumeClaim]
        secrets: list[AkriConnectorsSecret]
        stateful_set_configuration_settings: dict[str, Any]
        trust_settings: AkriConnectorTemplateTrustList

        @overload
        def __init__(
                self, 
                *, 
                additional_configuration: Optional[dict[str, str]] = ..., 
                allocation: Optional[AkriConnectorTemplateAllocation] = ..., 
                persistent_volume_claim_templates: Optional[list[dict[str, Any]]] = ..., 
                persistent_volume_claims: Optional[list[AkriConnectorTemplatePersistentVolumeClaim]] = ..., 
                secrets: Optional[list[AkriConnectorsSecret]] = ..., 
                stateful_set_configuration_settings: dict[str, Any], 
                trust_settings: Optional[AkriConnectorTemplateTrustList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorTemplateTrustList(_Model):
        trust_list_secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                trust_list_secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsContainerRegistry(AkriConnectorsRegistrySettings, discriminator='ContainerRegistry'):
        container_registry_settings: AkriConnectorsContainerRegistrySettings
        registry_settings_type: Literal[AkriConnectorsRegistrySettingsType.CONTAINER_REGISTRY]

        @overload
        def __init__(
                self, 
                *, 
                container_registry_settings: AkriConnectorsContainerRegistrySettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsContainerRegistrySettings(_Model):
        image_pull_secrets: Optional[list[AkriConnectorsImagePullSecret]]
        registry: str

        @overload
        def __init__(
                self, 
                *, 
                image_pull_secrets: Optional[list[AkriConnectorsImagePullSecret]] = ..., 
                registry: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsDiagnosticsLogs(_Model):
        level: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                level: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsDigest(AkriConnectorsTagDigestSettings, discriminator='Digest'):
        digest: str
        tag_digest_type: Literal[AkriConnectorsTagDigestType.DIGEST]

        @overload
        def __init__(
                self, 
                *, 
                digest: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsImagePullPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_NOT_PRESENT = "IfNotPresent"
        NEVER = "Never"


    class azure.mgmt.iotoperations.models.AkriConnectorsImagePullSecret(_Model):
        secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsMqttAuthentication(_Model):
        method: str

        @overload
        def __init__(
                self, 
                *, 
                method: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsMqttAuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_ACCOUNT_TOKEN = "ServiceAccountToken"


    class azure.mgmt.iotoperations.models.AkriConnectorsMqttConnectionConfiguration(_Model):
        authentication: Optional[AkriConnectorsMqttAuthentication]
        host: Optional[str]
        keep_alive_seconds: Optional[int]
        max_inflight_messages: Optional[int]
        protocol: Optional[Union[str, AkriConnectorsMqttProtocolType]]
        session_expiry_seconds: Optional[int]
        tls: Optional[TlsProperties]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AkriConnectorsMqttAuthentication] = ..., 
                host: Optional[str] = ..., 
                keep_alive_seconds: Optional[int] = ..., 
                max_inflight_messages: Optional[int] = ..., 
                protocol: Optional[Union[str, AkriConnectorsMqttProtocolType]] = ..., 
                session_expiry_seconds: Optional[int] = ..., 
                tls: Optional[TlsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsMqttProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MQTT = "Mqtt"


    class azure.mgmt.iotoperations.models.AkriConnectorsRegistryEndpointRef(AkriConnectorsRegistrySettings, discriminator='RegistryEndpointRef'):
        registry_endpoint_ref: str
        registry_settings_type: Literal[AkriConnectorsRegistrySettingsType.REGISTRY_ENDPOINT_REF]

        @overload
        def __init__(
                self, 
                *, 
                registry_endpoint_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsRegistrySettings(_Model):
        registry_settings_type: str

        @overload
        def __init__(
                self, 
                *, 
                registry_settings_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsRegistrySettingsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_REGISTRY = "ContainerRegistry"
        REGISTRY_ENDPOINT_REF = "RegistryEndpointRef"


    class azure.mgmt.iotoperations.models.AkriConnectorsSecret(_Model):
        secret_alias: str
        secret_key: str
        secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                secret_alias: str, 
                secret_key: str, 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsServiceAccountAuthentication(AkriConnectorsMqttAuthentication, discriminator='ServiceAccountToken'):
        method: Literal[AkriConnectorsMqttAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]
        service_account_token_settings: AkriConnectorsServiceAccountTokenSettings

        @overload
        def __init__(
                self, 
                *, 
                service_account_token_settings: AkriConnectorsServiceAccountTokenSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsServiceAccountTokenSettings(_Model):
        audience: str

        @overload
        def __init__(
                self, 
                *, 
                audience: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsTag(AkriConnectorsTagDigestSettings, discriminator='Tag'):
        tag: str
        tag_digest_type: Literal[AkriConnectorsTagDigestType.TAG]

        @overload
        def __init__(
                self, 
                *, 
                tag: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsTagDigestSettings(_Model):
        tag_digest_type: str

        @overload
        def __init__(
                self, 
                *, 
                tag_digest_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriConnectorsTagDigestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIGEST = "Digest"
        TAG = "Tag"


    class azure.mgmt.iotoperations.models.AkriServiceProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[AkriServiceStatus]


    class azure.mgmt.iotoperations.models.AkriServiceResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[AkriServiceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[AkriServiceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AkriServiceStatus(_Model):
        health_state: Optional[ResourceHealthStatus]


    class azure.mgmt.iotoperations.models.AuthorizationConfig(_Model):
        cache: Optional[Union[str, OperationalMode]]
        rules: Optional[list[AuthorizationRule]]

        @overload
        def __init__(
                self, 
                *, 
                cache: Optional[Union[str, OperationalMode]] = ..., 
                rules: Optional[list[AuthorizationRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AuthorizationRule(_Model):
        broker_resources: list[BrokerResourceRule]
        principals: PrincipalDefinition
        state_store_resources: Optional[list[StateStoreResourceRule]]

        @overload
        def __init__(
                self, 
                *, 
                broker_resources: list[BrokerResourceRule], 
                principals: PrincipalDefinition, 
                state_store_resources: Optional[list[StateStoreResourceRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.AzureDeviceRegistryNamespaceRef(_Model):
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BackendChain(_Model):
        partitions: int
        redundancy_factor: int
        workers: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                partitions: int, 
                redundancy_factor: int, 
                workers: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BatchingConfiguration(_Model):
        latency_seconds: Optional[int]
        max_messages: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                latency_seconds: Optional[int] = ..., 
                max_messages: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        SERVICE_ACCOUNT_TOKEN = "ServiceAccountToken"
        X509 = "X509"


    class azure.mgmt.iotoperations.models.BrokerAuthenticationProperties(_Model):
        authentication_methods: list[BrokerAuthenticatorMethods]
        health_state: Optional[Union[str, ResourceHealthState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                authentication_methods: list[BrokerAuthenticatorMethods]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticationResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[BrokerAuthenticationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[BrokerAuthenticationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticatorCustomAuth(_Model):
        x509: X509ManualCertificate

        @overload
        def __init__(
                self, 
                *, 
                x509: X509ManualCertificate
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticatorMethodCustom(_Model):
        auth: Optional[BrokerAuthenticatorCustomAuth]
        ca_cert_config_map: Optional[str]
        endpoint: str
        headers: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[BrokerAuthenticatorCustomAuth] = ..., 
                ca_cert_config_map: Optional[str] = ..., 
                endpoint: str, 
                headers: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticatorMethodSat(_Model):
        audiences: list[str]

        @overload
        def __init__(
                self, 
                *, 
                audiences: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticatorMethodX509(_Model):
        additional_validation: Optional[Union[str, BrokerAuthenticatorValidationMethods]]
        authorization_attributes: Optional[dict[str, BrokerAuthenticatorMethodX509Attributes]]
        trusted_client_ca_cert: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_validation: Optional[Union[str, BrokerAuthenticatorValidationMethods]] = ..., 
                authorization_attributes: Optional[dict[str, BrokerAuthenticatorMethodX509Attributes]] = ..., 
                trusted_client_ca_cert: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticatorMethodX509Attributes(_Model):
        attributes: dict[str, str]
        subject: str

        @overload
        def __init__(
                self, 
                *, 
                attributes: dict[str, str], 
                subject: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticatorMethods(_Model):
        custom_settings: Optional[BrokerAuthenticatorMethodCustom]
        method: Union[str, BrokerAuthenticationMethod]
        service_account_token_settings: Optional[BrokerAuthenticatorMethodSat]
        x509_settings: Optional[BrokerAuthenticatorMethodX509]

        @overload
        def __init__(
                self, 
                *, 
                custom_settings: Optional[BrokerAuthenticatorMethodCustom] = ..., 
                method: Union[str, BrokerAuthenticationMethod], 
                service_account_token_settings: Optional[BrokerAuthenticatorMethodSat] = ..., 
                x509_settings: Optional[BrokerAuthenticatorMethodX509] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthenticatorValidationMethods(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DEVICE_REGISTRY = "AzureDeviceRegistry"
        NONE = "None"


    class azure.mgmt.iotoperations.models.BrokerAuthorizationProperties(_Model):
        authorization_policies: AuthorizationConfig
        health_state: Optional[Union[str, ResourceHealthState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                authorization_policies: AuthorizationConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerAuthorizationResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[BrokerAuthorizationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[BrokerAuthorizationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerDiagnostics(_Model):
        logs: Optional[DiagnosticsLogs]
        metrics: Optional[Metrics]
        self_check: Optional[SelfCheck]
        traces: Optional[Traces]

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[DiagnosticsLogs] = ..., 
                metrics: Optional[Metrics] = ..., 
                self_check: Optional[SelfCheck] = ..., 
                traces: Optional[Traces] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerListenerProperties(_Model):
        health_state: Optional[Union[str, ResourceHealthState]]
        ports: list[ListenerPort]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        service_name: Optional[str]
        service_type: Optional[Union[str, ServiceType]]

        @overload
        def __init__(
                self, 
                *, 
                ports: list[ListenerPort], 
                service_name: Optional[str] = ..., 
                service_type: Optional[Union[str, ServiceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerListenerResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[BrokerListenerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[BrokerListenerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerMemoryProfile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        TINY = "Tiny"


    class azure.mgmt.iotoperations.models.BrokerPersistence(_Model):
        encryption: Optional[BrokerPersistenceEncryption]
        max_size: str
        persistent_volume_claim_spec: Optional[VolumeClaimSpec]
        retain: Optional[BrokerRetainMessagesPolicy]
        state_store: Optional[BrokerStateStorePolicy]
        subscriber_queue: Optional[BrokerSubscriberQueuePolicy]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[BrokerPersistenceEncryption] = ..., 
                max_size: str, 
                persistent_volume_claim_spec: Optional[VolumeClaimSpec] = ..., 
                retain: Optional[BrokerRetainMessagesPolicy] = ..., 
                state_store: Optional[BrokerStateStorePolicy] = ..., 
                subscriber_queue: Optional[BrokerSubscriberQueuePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerPersistenceEncryption(_Model):
        mode: Union[str, OperationalMode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, OperationalMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerPersistencePolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CUSTOM = "Custom"
        NONE = "None"


    class azure.mgmt.iotoperations.models.BrokerProperties(_Model):
        advanced: Optional[AdvancedSettings]
        cardinality: Optional[Cardinality]
        diagnostics: Optional[BrokerDiagnostics]
        disk_backed_message_buffer: Optional[DiskBackedMessageBuffer]
        generate_resource_limits: Optional[GenerateResourceLimits]
        health_state: Optional[Union[str, ResourceHealthState]]
        high_priority_messages_backpressure_handling: Optional[Union[str, HighPriorityMessagesBackpressureHandling]]
        memory_profile: Optional[Union[str, BrokerMemoryProfile]]
        persistence: Optional[BrokerPersistence]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[BrokerStatus]

        @overload
        def __init__(
                self, 
                *, 
                advanced: Optional[AdvancedSettings] = ..., 
                cardinality: Optional[Cardinality] = ..., 
                diagnostics: Optional[BrokerDiagnostics] = ..., 
                disk_backed_message_buffer: Optional[DiskBackedMessageBuffer] = ..., 
                generate_resource_limits: Optional[GenerateResourceLimits] = ..., 
                high_priority_messages_backpressure_handling: Optional[Union[str, HighPriorityMessagesBackpressureHandling]] = ..., 
                memory_profile: Optional[Union[str, BrokerMemoryProfile]] = ..., 
                persistence: Optional[BrokerPersistence] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MQTT = "Mqtt"
        WEB_SOCKETS = "WebSockets"


    class azure.mgmt.iotoperations.models.BrokerResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[BrokerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[BrokerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerResourceDefinitionMethods(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECT = "Connect"
        PUBLISH = "Publish"
        SUBSCRIBE = "Subscribe"


    class azure.mgmt.iotoperations.models.BrokerResourceRule(_Model):
        client_ids: Optional[list[str]]
        method: Union[str, BrokerResourceDefinitionMethods]
        topics: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                client_ids: Optional[list[str]] = ..., 
                method: Union[str, BrokerResourceDefinitionMethods], 
                topics: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerRetainMessagesCustomPolicy(BrokerRetainMessagesPolicy, discriminator='Custom'):
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        retain_settings: BrokerRetainMessagesSettings

        @overload
        def __init__(
                self, 
                *, 
                retain_settings: BrokerRetainMessagesSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerRetainMessagesDynamic(_Model):
        mode: Union[str, OperationalMode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, OperationalMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerRetainMessagesPolicy(_Model):
        mode: str

        @overload
        def __init__(
                self, 
                *, 
                mode: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerRetainMessagesSettings(_Model):
        dynamic: Optional[BrokerRetainMessagesDynamic]
        topics: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic: Optional[BrokerRetainMessagesDynamic] = ..., 
                topics: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerStateStoreCustomPolicy(BrokerStateStorePolicy, discriminator='Custom'):
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        state_store_settings: BrokerStateStorePolicySettings

        @overload
        def __init__(
                self, 
                *, 
                state_store_settings: BrokerStateStorePolicySettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerStateStoreDynamic(_Model):
        mode: Union[str, OperationalMode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, OperationalMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerStateStoreKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY = "Binary"
        PATTERN = "Pattern"
        STRING = "String"


    class azure.mgmt.iotoperations.models.BrokerStateStorePolicy(_Model):
        mode: str

        @overload
        def __init__(
                self, 
                *, 
                mode: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerStateStorePolicyResources(_Model):
        key_type: Union[str, BrokerStateStoreKeyType]
        keys_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                key_type: Union[str, BrokerStateStoreKeyType], 
                keys_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerStateStorePolicySettings(_Model):
        dynamic: Optional[BrokerStateStoreDynamic]
        state_store_resources: Optional[list[BrokerStateStorePolicyResources]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic: Optional[BrokerStateStoreDynamic] = ..., 
                state_store_resources: Optional[list[BrokerStateStorePolicyResources]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerStatus(_Model):
        health_state: Optional[ResourceHealthStatus]


    class azure.mgmt.iotoperations.models.BrokerSubscriberQueueCustomPolicy(BrokerSubscriberQueuePolicy, discriminator='Custom'):
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        subscriber_queue_settings: BrokerSubscriberQueueCustomPolicySettings

        @overload
        def __init__(
                self, 
                *, 
                subscriber_queue_settings: BrokerSubscriberQueueCustomPolicySettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerSubscriberQueueCustomPolicySettings(_Model):
        dynamic: Optional[BrokerSubscriberQueueDynamic]
        subscriber_client_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dynamic: Optional[BrokerSubscriberQueueDynamic] = ..., 
                subscriber_client_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerSubscriberQueueDynamic(_Model):
        mode: Union[str, OperationalMode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, OperationalMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.BrokerSubscriberQueuePolicy(_Model):
        mode: str

        @overload
        def __init__(
                self, 
                *, 
                mode: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.Cardinality(_Model):
        backend_chain: BackendChain
        frontend: Frontend

        @overload
        def __init__(
                self, 
                *, 
                backend_chain: BackendChain, 
                frontend: Frontend
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.CertManagerCertOptions(_Model):
        duration: str
        private_key: CertManagerPrivateKey
        renew_before: str

        @overload
        def __init__(
                self, 
                *, 
                duration: str, 
                private_key: CertManagerPrivateKey, 
                renew_before: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.CertManagerCertificateSpec(_Model):
        duration: Optional[str]
        issuer_ref: CertManagerIssuerRef
        private_key: Optional[CertManagerPrivateKey]
        renew_before: Optional[str]
        san: Optional[SanForCert]
        secret_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[str] = ..., 
                issuer_ref: CertManagerIssuerRef, 
                private_key: Optional[CertManagerPrivateKey] = ..., 
                renew_before: Optional[str] = ..., 
                san: Optional[SanForCert] = ..., 
                secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.CertManagerIssuerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER_ISSUER = "ClusterIssuer"
        ISSUER = "Issuer"


    class azure.mgmt.iotoperations.models.CertManagerIssuerRef(_Model):
        group: str
        kind: Union[str, CertManagerIssuerKind]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                group: str, 
                kind: Union[str, CertManagerIssuerKind], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.CertManagerPrivateKey(_Model):
        algorithm: Union[str, PrivateKeyAlgorithm]
        rotation_policy: Union[str, PrivateKeyRotationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                algorithm: Union[str, PrivateKeyAlgorithm], 
                rotation_policy: Union[str, PrivateKeyRotationPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.ClientConfig(_Model):
        max_keep_alive_seconds: Optional[int]
        max_message_expiry_seconds: Optional[int]
        max_packet_size_bytes: Optional[int]
        max_receive_maximum: Optional[int]
        max_session_expiry_seconds: Optional[int]
        subscriber_queue_limit: Optional[SubscriberQueueLimit]

        @overload
        def __init__(
                self, 
                *, 
                max_keep_alive_seconds: Optional[int] = ..., 
                max_message_expiry_seconds: Optional[int] = ..., 
                max_packet_size_bytes: Optional[int] = ..., 
                max_receive_maximum: Optional[int] = ..., 
                max_session_expiry_seconds: Optional[int] = ..., 
                subscriber_queue_limit: Optional[SubscriberQueueLimit] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.CloudEventAttributeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_OR_REMAP = "CreateOrRemap"
        PROPAGATE = "Propagate"


    class azure.mgmt.iotoperations.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.iotoperations.models.DataExplorerAuthMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"


    class azure.mgmt.iotoperations.models.DataLakeStorageAuthMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_TOKEN = "AccessToken"
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"


    class azure.mgmt.iotoperations.models.DataflowBuiltInTransformationDataset(_Model):
        description: Optional[str]
        expression: Optional[str]
        inputs: list[str]
        key: str
        schema_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                inputs: list[str], 
                key: str, 
                schema_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowBuiltInTransformationFilter(_Model):
        description: Optional[str]
        expression: str
        inputs: list[str]
        type: Optional[Union[str, FilterType]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                expression: str, 
                inputs: list[str], 
                type: Optional[Union[str, FilterType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowBuiltInTransformationMap(_Model):
        description: Optional[str]
        expression: Optional[str]
        inputs: list[str]
        output: str
        type: Optional[Union[str, DataflowMappingType]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                inputs: list[str], 
                output: str, 
                type: Optional[Union[str, DataflowMappingType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowBuiltInTransformationSettings(_Model):
        datasets: Optional[list[DataflowBuiltInTransformationDataset]]
        filter: Optional[list[DataflowBuiltInTransformationFilter]]
        map: Optional[list[DataflowBuiltInTransformationMap]]
        schema_ref: Optional[str]
        serialization_format: Optional[Union[str, TransformationSerializationFormat]]

        @overload
        def __init__(
                self, 
                *, 
                datasets: Optional[list[DataflowBuiltInTransformationDataset]] = ..., 
                filter: Optional[list[DataflowBuiltInTransformationFilter]] = ..., 
                map: Optional[list[DataflowBuiltInTransformationMap]] = ..., 
                schema_ref: Optional[str] = ..., 
                serialization_format: Optional[Union[str, TransformationSerializationFormat]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowDestinationAddIfNotPresentHeaderAction(DataflowDestinationHeaderAction, discriminator='AddIfNotPresent'):
        action_type: Literal[DataflowHeaderActionType.ADD_IF_NOT_PRESENT]
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


    class azure.mgmt.iotoperations.models.DataflowDestinationAddOrReplaceHeaderAction(DataflowDestinationHeaderAction, discriminator='AddOrReplace'):
        action_type: Literal[DataflowHeaderActionType.ADD_OR_REPLACE]
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


    class azure.mgmt.iotoperations.models.DataflowDestinationHeaderAction(_Model):
        action_type: str

        @overload
        def __init__(
                self, 
                *, 
                action_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowDestinationOperationSettings(_Model):
        data_destination: str
        endpoint_ref: str
        headers: Optional[list[DataflowDestinationHeaderAction]]

        @overload
        def __init__(
                self, 
                *, 
                data_destination: str, 
                endpoint_ref: str, 
                headers: Optional[list[DataflowDestinationHeaderAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowDestinationRemoveHeaderAction(DataflowDestinationHeaderAction, discriminator='Remove'):
        action_type: Literal[DataflowHeaderActionType.REMOVE]
        key: str

        @overload
        def __init__(
                self, 
                *, 
                key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationAccessToken(_Model):
        secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationAnonymous(_Model):


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationSasl(_Model):
        sasl_type: Union[str, DataflowEndpointAuthenticationSaslType]
        secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                sasl_type: Union[str, DataflowEndpointAuthenticationSaslType], 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationSaslType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLAIN = "Plain"
        SCRAM_SHA256 = "ScramSha256"
        SCRAM_SHA512 = "ScramSha512"


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationServiceAccountToken(_Model):
        audience: str

        @overload
        def __init__(
                self, 
                *, 
                audience: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationSystemAssignedManagedIdentity(_Model):
        audience: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                audience: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationUserAssignedManagedIdentity(_Model):
        client_id: str
        scope: Optional[str]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                scope: Optional[str] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointAuthenticationX509(_Model):
        secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointDataExplorer(_Model):
        authentication: DataflowEndpointDataExplorerAuthentication
        batching: Optional[BatchingConfiguration]
        database: str
        host: str

        @overload
        def __init__(
                self, 
                *, 
                authentication: DataflowEndpointDataExplorerAuthentication, 
                batching: Optional[BatchingConfiguration] = ..., 
                database: str, 
                host: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointDataExplorerAuthentication(_Model):
        method: Union[str, DataExplorerAuthMethod]
        system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity]
        user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                method: Union[str, DataExplorerAuthMethod], 
                system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity] = ..., 
                user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointDataLakeStorage(_Model):
        authentication: DataflowEndpointDataLakeStorageAuthentication
        batching: Optional[BatchingConfiguration]
        host: str

        @overload
        def __init__(
                self, 
                *, 
                authentication: DataflowEndpointDataLakeStorageAuthentication, 
                batching: Optional[BatchingConfiguration] = ..., 
                host: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointDataLakeStorageAuthentication(_Model):
        access_token_settings: Optional[DataflowEndpointAuthenticationAccessToken]
        method: Union[str, DataLakeStorageAuthMethod]
        system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity]
        user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                access_token_settings: Optional[DataflowEndpointAuthenticationAccessToken] = ..., 
                method: Union[str, DataLakeStorageAuthMethod], 
                system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity] = ..., 
                user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointFabricOneLake(_Model):
        authentication: DataflowEndpointFabricOneLakeAuthentication
        batching: Optional[BatchingConfiguration]
        host: str
        names: DataflowEndpointFabricOneLakeNames
        one_lake_path_type: Union[str, DataflowEndpointFabricPathType]

        @overload
        def __init__(
                self, 
                *, 
                authentication: DataflowEndpointFabricOneLakeAuthentication, 
                batching: Optional[BatchingConfiguration] = ..., 
                host: str, 
                names: DataflowEndpointFabricOneLakeNames, 
                one_lake_path_type: Union[str, DataflowEndpointFabricPathType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointFabricOneLakeAuthentication(_Model):
        method: Union[str, FabricOneLakeAuthMethod]
        system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity]
        user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                method: Union[str, FabricOneLakeAuthMethod], 
                system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity] = ..., 
                user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointFabricOneLakeNames(_Model):
        lakehouse_name: str
        workspace_name: str

        @overload
        def __init__(
                self, 
                *, 
                lakehouse_name: str, 
                workspace_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointFabricPathType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILES = "Files"
        TABLES = "Tables"


    class azure.mgmt.iotoperations.models.DataflowEndpointHostType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_KAFKA = "CustomKafka"
        CUSTOM_MQTT = "CustomMqtt"
        EVENTHUB = "Eventhub"
        EVENT_GRID = "EventGrid"
        FABRIC_RT = "FabricRT"
        LOCAL_BROKER = "LocalBroker"


    class azure.mgmt.iotoperations.models.DataflowEndpointKafka(_Model):
        authentication: DataflowEndpointKafkaAuthentication
        batching: Optional[DataflowEndpointKafkaBatching]
        cloud_event_attributes: Optional[Union[str, CloudEventAttributeType]]
        compression: Optional[Union[str, DataflowEndpointKafkaCompression]]
        consumer_group_id: Optional[str]
        copy_mqtt_properties: Optional[Union[str, OperationalMode]]
        host: str
        kafka_acks: Optional[Union[str, DataflowEndpointKafkaAcks]]
        partition_strategy: Optional[Union[str, DataflowEndpointKafkaPartitionStrategy]]
        tls: Optional[TlsProperties]

        @overload
        def __init__(
                self, 
                *, 
                authentication: DataflowEndpointKafkaAuthentication, 
                batching: Optional[DataflowEndpointKafkaBatching] = ..., 
                cloud_event_attributes: Optional[Union[str, CloudEventAttributeType]] = ..., 
                compression: Optional[Union[str, DataflowEndpointKafkaCompression]] = ..., 
                consumer_group_id: Optional[str] = ..., 
                copy_mqtt_properties: Optional[Union[str, OperationalMode]] = ..., 
                host: str, 
                kafka_acks: Optional[Union[str, DataflowEndpointKafkaAcks]] = ..., 
                partition_strategy: Optional[Union[str, DataflowEndpointKafkaPartitionStrategy]] = ..., 
                tls: Optional[TlsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointKafkaAcks(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ONE = "One"
        ZERO = "Zero"


    class azure.mgmt.iotoperations.models.DataflowEndpointKafkaAuthentication(_Model):
        method: Union[str, KafkaAuthMethod]
        sasl_settings: Optional[DataflowEndpointAuthenticationSasl]
        system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity]
        user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity]
        x509_certificate_settings: Optional[DataflowEndpointAuthenticationX509]

        @overload
        def __init__(
                self, 
                *, 
                method: Union[str, KafkaAuthMethod], 
                sasl_settings: Optional[DataflowEndpointAuthenticationSasl] = ..., 
                system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity] = ..., 
                user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity] = ..., 
                x509_certificate_settings: Optional[DataflowEndpointAuthenticationX509] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointKafkaBatching(_Model):
        latency_ms: Optional[int]
        max_bytes: Optional[int]
        max_messages: Optional[int]
        mode: Optional[Union[str, OperationalMode]]

        @overload
        def __init__(
                self, 
                *, 
                latency_ms: Optional[int] = ..., 
                max_bytes: Optional[int] = ..., 
                max_messages: Optional[int] = ..., 
                mode: Optional[Union[str, OperationalMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointKafkaCompression(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GZIP = "Gzip"
        LZ4 = "Lz4"
        NONE = "None"
        SNAPPY = "Snappy"


    class azure.mgmt.iotoperations.models.DataflowEndpointKafkaPartitionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        PROPERTY = "Property"
        STATIC = "Static"
        TOPIC = "Topic"


    class azure.mgmt.iotoperations.models.DataflowEndpointLocalStorage(_Model):
        persistent_volume_claim_ref: str

        @overload
        def __init__(
                self, 
                *, 
                persistent_volume_claim_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointMqtt(_Model):
        authentication: DataflowEndpointMqttAuthentication
        client_id_prefix: Optional[str]
        cloud_event_attributes: Optional[Union[str, CloudEventAttributeType]]
        host: Optional[str]
        keep_alive_seconds: Optional[int]
        max_inflight_messages: Optional[int]
        protocol: Optional[Union[str, BrokerProtocolType]]
        qos: Optional[int]
        retain: Optional[Union[str, MqttRetainType]]
        session_expiry_seconds: Optional[int]
        tls: Optional[TlsProperties]

        @overload
        def __init__(
                self, 
                *, 
                authentication: DataflowEndpointMqttAuthentication, 
                client_id_prefix: Optional[str] = ..., 
                cloud_event_attributes: Optional[Union[str, CloudEventAttributeType]] = ..., 
                host: Optional[str] = ..., 
                keep_alive_seconds: Optional[int] = ..., 
                max_inflight_messages: Optional[int] = ..., 
                protocol: Optional[Union[str, BrokerProtocolType]] = ..., 
                qos: Optional[int] = ..., 
                retain: Optional[Union[str, MqttRetainType]] = ..., 
                session_expiry_seconds: Optional[int] = ..., 
                tls: Optional[TlsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointMqttAuthentication(_Model):
        method: Union[str, MqttAuthMethod]
        service_account_token_settings: Optional[DataflowEndpointAuthenticationServiceAccountToken]
        system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity]
        user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity]
        x509_certificate_settings: Optional[DataflowEndpointAuthenticationX509]

        @overload
        def __init__(
                self, 
                *, 
                method: Union[str, MqttAuthMethod], 
                service_account_token_settings: Optional[DataflowEndpointAuthenticationServiceAccountToken] = ..., 
                system_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationSystemAssignedManagedIdentity] = ..., 
                user_assigned_managed_identity_settings: Optional[DataflowEndpointAuthenticationUserAssignedManagedIdentity] = ..., 
                x509_certificate_settings: Optional[DataflowEndpointAuthenticationX509] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointOpenTelemetry(_Model):
        authentication: DataflowOpenTelemetryAuthentication
        batching: Optional[BatchingConfiguration]
        host: str
        tls: Optional[TlsProperties]

        @overload
        def __init__(
                self, 
                *, 
                authentication: DataflowOpenTelemetryAuthentication, 
                batching: Optional[BatchingConfiguration] = ..., 
                host: str, 
                tls: Optional[TlsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointProperties(_Model):
        data_explorer_settings: Optional[DataflowEndpointDataExplorer]
        data_lake_storage_settings: Optional[DataflowEndpointDataLakeStorage]
        endpoint_type: Union[str, EndpointType]
        fabric_one_lake_settings: Optional[DataflowEndpointFabricOneLake]
        health_state: Optional[Union[str, ResourceHealthState]]
        host_type: Optional[Union[str, DataflowEndpointHostType]]
        kafka_settings: Optional[DataflowEndpointKafka]
        local_storage_settings: Optional[DataflowEndpointLocalStorage]
        mqtt_settings: Optional[DataflowEndpointMqtt]
        open_telemetry_settings: Optional[DataflowEndpointOpenTelemetry]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                data_explorer_settings: Optional[DataflowEndpointDataExplorer] = ..., 
                data_lake_storage_settings: Optional[DataflowEndpointDataLakeStorage] = ..., 
                endpoint_type: Union[str, EndpointType], 
                fabric_one_lake_settings: Optional[DataflowEndpointFabricOneLake] = ..., 
                host_type: Optional[Union[str, DataflowEndpointHostType]] = ..., 
                kafka_settings: Optional[DataflowEndpointKafka] = ..., 
                local_storage_settings: Optional[DataflowEndpointLocalStorage] = ..., 
                mqtt_settings: Optional[DataflowEndpointMqtt] = ..., 
                open_telemetry_settings: Optional[DataflowEndpointOpenTelemetry] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowEndpointResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[DataflowEndpointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[DataflowEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphConnectionInput(_Model):
        name: str
        schema: Optional[DataflowGraphConnectionSchemaSettings]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                schema: Optional[DataflowGraphConnectionSchemaSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphConnectionOutput(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphConnectionSchemaSerializationFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "Avro"
        DELTA = "Delta"
        JSON = "Json"
        PARQUET = "Parquet"


    class azure.mgmt.iotoperations.models.DataflowGraphConnectionSchemaSettings(_Model):
        schema_ref: Optional[str]
        serialization_format: Optional[Union[str, DataflowGraphConnectionSchemaSerializationFormat]]

        @overload
        def __init__(
                self, 
                *, 
                schema_ref: Optional[str] = ..., 
                serialization_format: Optional[Union[str, DataflowGraphConnectionSchemaSerializationFormat]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphDestinationAddIfNotPresentHeaderAction(DataflowGraphDestinationHeaderAction, discriminator='AddIfNotPresent'):
        action_type: Literal[DataflowGraphDestinationHeaderActionType.ADD_IF_NOT_PRESENT]
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


    class azure.mgmt.iotoperations.models.DataflowGraphDestinationAddOrReplaceHeaderAction(DataflowGraphDestinationHeaderAction, discriminator='AddOrReplace'):
        action_type: Literal[DataflowGraphDestinationHeaderActionType.ADD_OR_REPLACE]
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


    class azure.mgmt.iotoperations.models.DataflowGraphDestinationHeaderAction(_Model):
        action_type: str

        @overload
        def __init__(
                self, 
                *, 
                action_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphDestinationHeaderActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_IF_NOT_PRESENT = "AddIfNotPresent"
        ADD_OR_REPLACE = "AddOrReplace"
        REMOVE = "Remove"


    class azure.mgmt.iotoperations.models.DataflowGraphDestinationNode(DataflowGraphNode, discriminator='Destination'):
        destination_settings: DataflowGraphDestinationNodeSettings
        name: str
        node_type: Literal[DataflowGraphNodeType.DESTINATION]

        @overload
        def __init__(
                self, 
                *, 
                destination_settings: DataflowGraphDestinationNodeSettings, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphDestinationNodeSettings(_Model):
        data_destination: str
        endpoint_ref: str
        headers: Optional[list[DataflowGraphDestinationHeaderAction]]

        @overload
        def __init__(
                self, 
                *, 
                data_destination: str, 
                endpoint_ref: str, 
                headers: Optional[list[DataflowGraphDestinationHeaderAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphDestinationRemoveHeaderAction(DataflowGraphDestinationHeaderAction, discriminator='Remove'):
        action_type: Literal[DataflowGraphDestinationHeaderActionType.REMOVE]
        key: str

        @overload
        def __init__(
                self, 
                *, 
                key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphGraphNode(DataflowGraphNode, discriminator='Graph'):
        graph_settings: DataflowGraphNodeGraphSettings
        name: str
        node_type: Literal[DataflowGraphNodeType.GRAPH]

        @overload
        def __init__(
                self, 
                *, 
                graph_settings: DataflowGraphNodeGraphSettings, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphGraphNodeConfiguration(_Model):
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


    class azure.mgmt.iotoperations.models.DataflowGraphNode(_Model):
        name: str
        node_type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                node_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphNodeConnection(_Model):
        from_property: DataflowGraphConnectionInput
        to: DataflowGraphConnectionOutput

        @overload
        def __init__(
                self, 
                *, 
                from_property: DataflowGraphConnectionInput, 
                to: DataflowGraphConnectionOutput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphNodeGraphSettings(_Model):
        artifact: str
        configuration: Optional[list[DataflowGraphGraphNodeConfiguration]]
        registry_endpoint_ref: str

        @overload
        def __init__(
                self, 
                *, 
                artifact: str, 
                configuration: Optional[list[DataflowGraphGraphNodeConfiguration]] = ..., 
                registry_endpoint_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphNodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESTINATION = "Destination"
        GRAPH = "Graph"
        SOURCE = "Source"


    class azure.mgmt.iotoperations.models.DataflowGraphProperties(_Model):
        health_state: Optional[Union[str, ResourceHealthState]]
        mode: Optional[Union[str, OperationalMode]]
        node_connections: list[DataflowGraphNodeConnection]
        nodes: list[DataflowGraphNode]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_disk_persistence: Optional[Union[str, OperationalMode]]
        status: Optional[DataflowGraphStatus]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, OperationalMode]] = ..., 
                node_connections: list[DataflowGraphNodeConnection], 
                nodes: list[DataflowGraphNode], 
                request_disk_persistence: Optional[Union[str, OperationalMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[DataflowGraphProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[DataflowGraphProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphSourceNode(DataflowGraphNode, discriminator='Source'):
        name: str
        node_type: Literal[DataflowGraphNodeType.SOURCE]
        source_settings: DataflowGraphSourceSettings

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                source_settings: DataflowGraphSourceSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphSourceSettings(_Model):
        asset_ref: Optional[str]
        data_sources: list[str]
        endpoint_ref: str

        @overload
        def __init__(
                self, 
                *, 
                asset_ref: Optional[str] = ..., 
                data_sources: list[str], 
                endpoint_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowGraphStatus(_Model):
        health_state: Optional[ResourceHealthStatus]


    class azure.mgmt.iotoperations.models.DataflowHeaderActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_IF_NOT_PRESENT = "AddIfNotPresent"
        ADD_OR_REPLACE = "AddOrReplace"
        REMOVE = "Remove"


    class azure.mgmt.iotoperations.models.DataflowMappingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN_FUNCTION = "BuiltInFunction"
        COMPUTE = "Compute"
        NEW_PROPERTIES = "NewProperties"
        PASS_THROUGH = "PassThrough"
        RENAME = "Rename"


    class azure.mgmt.iotoperations.models.DataflowOpenTelemetryAnonymousAuthentication(DataflowOpenTelemetryAuthentication, discriminator='Anonymous'):
        anonymous_settings: DataflowEndpointAuthenticationAnonymous
        method: Literal[DataflowOpenTelemetryAuthenticationMethod.ANONYMOUS]

        @overload
        def __init__(
                self, 
                *, 
                anonymous_settings: DataflowEndpointAuthenticationAnonymous
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowOpenTelemetryAuthentication(_Model):
        method: str

        @overload
        def __init__(
                self, 
                *, 
                method: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowOpenTelemetryAuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "Anonymous"
        SERVICE_ACCOUNT_TOKEN = "ServiceAccountToken"
        X509_CERTIFICATE = "X509Certificate"


    class azure.mgmt.iotoperations.models.DataflowOpenTelemetryServiceAccountAuthentication(DataflowOpenTelemetryAuthentication, discriminator='ServiceAccountToken'):
        method: Literal[DataflowOpenTelemetryAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]
        service_account_token_settings: DataflowEndpointAuthenticationServiceAccountToken

        @overload
        def __init__(
                self, 
                *, 
                service_account_token_settings: DataflowEndpointAuthenticationServiceAccountToken
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowOpenTelemetryX509CertificateAuthentication(DataflowOpenTelemetryAuthentication, discriminator='X509Certificate'):
        method: Literal[DataflowOpenTelemetryAuthenticationMethod.X509_CERTIFICATE]
        x509_certificate_settings: DataflowEndpointAuthenticationX509

        @overload
        def __init__(
                self, 
                *, 
                x509_certificate_settings: DataflowEndpointAuthenticationX509
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowOperation(_Model):
        built_in_transformation_settings: Optional[DataflowBuiltInTransformationSettings]
        destination_settings: Optional[DataflowDestinationOperationSettings]
        name: Optional[str]
        operation_type: Union[str, OperationType]
        source_settings: Optional[DataflowSourceOperationSettings]

        @overload
        def __init__(
                self, 
                *, 
                built_in_transformation_settings: Optional[DataflowBuiltInTransformationSettings] = ..., 
                destination_settings: Optional[DataflowDestinationOperationSettings] = ..., 
                name: Optional[str] = ..., 
                operation_type: Union[str, OperationType], 
                source_settings: Optional[DataflowSourceOperationSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowProfileProperties(_Model):
        diagnostics: Optional[ProfileDiagnostics]
        health_state: Optional[Union[str, ResourceHealthState]]
        instance_count: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[DataflowProfileStatus]

        @overload
        def __init__(
                self, 
                *, 
                diagnostics: Optional[ProfileDiagnostics] = ..., 
                instance_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowProfileResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[DataflowProfileProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[DataflowProfileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowProfileStatus(_Model):
        health_state: Optional[ResourceHealthStatus]


    class azure.mgmt.iotoperations.models.DataflowProperties(_Model):
        health_state: Optional[Union[str, ResourceHealthState]]
        mode: Optional[Union[str, OperationalMode]]
        operations: list[DataflowOperation]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_disk_persistence: Optional[Union[str, OperationalMode]]
        status: Optional[DataflowStatus]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, OperationalMode]] = ..., 
                operations: list[DataflowOperation], 
                request_disk_persistence: Optional[Union[str, OperationalMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[DataflowProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[DataflowProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowSourceOperationSettings(_Model):
        asset_ref: Optional[str]
        data_sources: list[str]
        endpoint_ref: str
        schema_ref: Optional[str]
        serialization_format: Optional[Union[str, SourceSerializationFormat]]

        @overload
        def __init__(
                self, 
                *, 
                asset_ref: Optional[str] = ..., 
                data_sources: list[str], 
                endpoint_ref: str, 
                schema_ref: Optional[str] = ..., 
                serialization_format: Optional[Union[str, SourceSerializationFormat]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DataflowStatus(_Model):
        health_state: Optional[ResourceHealthStatus]


    class azure.mgmt.iotoperations.models.DiagnosticsLogs(_Model):
        level: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                level: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.DiskBackedMessageBuffer(_Model):
        ephemeral_volume_claim_spec: Optional[VolumeClaimSpec]
        max_size: str
        persistent_volume_claim_spec: Optional[VolumeClaimSpec]

        @overload
        def __init__(
                self, 
                *, 
                ephemeral_volume_claim_spec: Optional[VolumeClaimSpec] = ..., 
                max_size: str, 
                persistent_volume_claim_spec: Optional[VolumeClaimSpec] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_EXPLORER = "DataExplorer"
        DATA_LAKE_STORAGE = "DataLakeStorage"
        FABRIC_ONE_LAKE = "FabricOneLake"
        KAFKA = "Kafka"
        LOCAL_STORAGE = "LocalStorage"
        MQTT = "Mqtt"
        OPEN_TELEMETRY = "OpenTelemetry"


    class azure.mgmt.iotoperations.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.iotoperations.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.iotoperations.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.ExtendedLocation(_Model):
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


    class azure.mgmt.iotoperations.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"


    class azure.mgmt.iotoperations.models.FabricOneLakeAuthMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"


    class azure.mgmt.iotoperations.models.FilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILTER = "Filter"


    class azure.mgmt.iotoperations.models.Frontend(_Model):
        replicas: int
        workers: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                replicas: int, 
                workers: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.GenerateResourceLimits(_Model):
        cpu: Optional[Union[str, OperationalMode]]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[Union[str, OperationalMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.HighPriorityMessagesBackpressureHandling(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPT = "Accept"
        REJECT = "Reject"


    class azure.mgmt.iotoperations.models.InstanceFeature(_Model):
        mode: Optional[Union[str, InstanceFeatureMode]]
        settings: Optional[dict[str, Union[str, OperationalMode]]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, InstanceFeatureMode]] = ..., 
                settings: Optional[dict[str, Union[str, OperationalMode]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.InstanceFeatureMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        PREVIEW = "Preview"
        STABLE = "Stable"


    class azure.mgmt.iotoperations.models.InstancePatchModel(_Model):
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


    class azure.mgmt.iotoperations.models.InstanceProperties(_Model):
        adr_namespace_ref: Optional[AzureDeviceRegistryNamespaceRef]
        default_secret_provider_class_ref: Optional[SecretProviderClassRef]
        description: Optional[str]
        features: Optional[dict[str, InstanceFeature]]
        health_state: Optional[Union[str, ResourceHealthState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        schema_registry_ref: SchemaRegistryRef
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                adr_namespace_ref: Optional[AzureDeviceRegistryNamespaceRef] = ..., 
                default_secret_provider_class_ref: Optional[SecretProviderClassRef] = ..., 
                description: Optional[str] = ..., 
                features: Optional[dict[str, InstanceFeature]] = ..., 
                schema_registry_ref: SchemaRegistryRef
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.InstanceResource(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[InstanceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[InstanceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.KafkaAuthMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "Anonymous"
        SASL = "Sasl"
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"
        X509_CERTIFICATE = "X509Certificate"


    class azure.mgmt.iotoperations.models.KubernetesReference(_Model):
        api_group: Optional[str]
        kind: str
        name: str
        namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_group: Optional[str] = ..., 
                kind: str, 
                name: str, 
                namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.ListenerPort(_Model):
        authentication_ref: Optional[str]
        authorization_ref: Optional[str]
        node_port: Optional[int]
        port: int
        protocol: Optional[Union[str, BrokerProtocolType]]
        tls: Optional[TlsCertMethod]

        @overload
        def __init__(
                self, 
                *, 
                authentication_ref: Optional[str] = ..., 
                authorization_ref: Optional[str] = ..., 
                node_port: Optional[int] = ..., 
                port: int, 
                protocol: Optional[Union[str, BrokerProtocolType]] = ..., 
                tls: Optional[TlsCertMethod] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.LocalKubernetesReference(_Model):
        api_group: Optional[str]
        kind: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                api_group: Optional[str] = ..., 
                kind: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.iotoperations.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.iotoperations.models.Metrics(_Model):
        prometheus_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                prometheus_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.MqttAuthMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "Anonymous"
        SERVICE_ACCOUNT_TOKEN = "ServiceAccountToken"
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"
        X509_CERTIFICATE = "X509Certificate"


    class azure.mgmt.iotoperations.models.MqttRetainType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEEP = "Keep"
        NEVER = "Never"


    class azure.mgmt.iotoperations.models.Operation(_Model):
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


    class azure.mgmt.iotoperations.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.iotoperations.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN_TRANSFORMATION = "BuiltInTransformation"
        DESTINATION = "Destination"
        SOURCE = "Source"


    class azure.mgmt.iotoperations.models.OperationalMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.iotoperations.models.OperatorValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOES_NOT_EXIST = "DoesNotExist"
        EXISTS = "Exists"
        IN = "In"
        NOT_IN = "NotIn"


    class azure.mgmt.iotoperations.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.iotoperations.models.PrincipalDefinition(_Model):
        attributes: Optional[list[dict[str, str]]]
        client_ids: Optional[list[str]]
        usernames: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[list[dict[str, str]]] = ..., 
                client_ids: Optional[list[str]] = ..., 
                usernames: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.PrivateKeyAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EC256 = "Ec256"
        EC384 = "Ec384"
        EC521 = "Ec521"
        ED25519 = "Ed25519"
        RSA2048 = "Rsa2048"
        RSA4096 = "Rsa4096"
        RSA8192 = "Rsa8192"


    class azure.mgmt.iotoperations.models.PrivateKeyRotationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        NEVER = "Never"


    class azure.mgmt.iotoperations.models.ProfileDiagnostics(_Model):
        logs: Optional[DiagnosticsLogs]
        metrics: Optional[Metrics]

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[DiagnosticsLogs] = ..., 
                metrics: Optional[Metrics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.iotoperations.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.models.RegistryEndpointAnonymousAuthentication(RegistryEndpointAuthentication, discriminator='Anonymous'):
        anonymous_settings: RegistryEndpointAnonymousSettings
        method: Literal[RegistryEndpointAuthenticationMethod.ANONYMOUS]

        @overload
        def __init__(
                self, 
                *, 
                anonymous_settings: RegistryEndpointAnonymousSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointAnonymousSettings(_Model):


    class azure.mgmt.iotoperations.models.RegistryEndpointArtifactPullSecretAuthentication(RegistryEndpointAuthentication, discriminator='ArtifactPullSecret'):
        artifact_pull_secret_settings: RegistryEndpointArtifactPullSecretSettings
        method: Literal[RegistryEndpointAuthenticationMethod.ARTIFACT_PULL_SECRET]

        @overload
        def __init__(
                self, 
                *, 
                artifact_pull_secret_settings: RegistryEndpointArtifactPullSecretSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointArtifactPullSecretSettings(_Model):
        secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointAuthentication(_Model):
        method: str

        @overload
        def __init__(
                self, 
                *, 
                method: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointAuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "Anonymous"
        ARTIFACT_PULL_SECRET = "ArtifactPullSecret"
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"


    class azure.mgmt.iotoperations.models.RegistryEndpointProperties(_Model):
        authentication: RegistryEndpointAuthentication
        code_signing_cas: Optional[list[RegistryEndpointTrustedSigningKey]]
        health_state: Optional[Union[str, ResourceHealthState]]
        host: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                authentication: RegistryEndpointAuthentication, 
                code_signing_cas: Optional[list[RegistryEndpointTrustedSigningKey]] = ..., 
                host: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointResource(ProxyResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        name: str
        properties: Optional[RegistryEndpointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                properties: Optional[RegistryEndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointSystemAssignedIdentityAuthentication(RegistryEndpointAuthentication, discriminator='SystemAssignedManagedIdentity'):
        method: Literal[RegistryEndpointAuthenticationMethod.SYSTEM_ASSIGNED_MANAGED_IDENTITY]
        system_assigned_managed_identity_settings: RegistryEndpointSystemAssignedManagedIdentitySettings

        @overload
        def __init__(
                self, 
                *, 
                system_assigned_managed_identity_settings: RegistryEndpointSystemAssignedManagedIdentitySettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointSystemAssignedManagedIdentitySettings(_Model):
        audience: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                audience: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointTrustedSigningKey(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointTrustedSigningKeyConfigMap(RegistryEndpointTrustedSigningKey, discriminator='ConfigMap'):
        config_map_ref: str
        type: Literal[RegistryEndpointTrustedSigningKeyType.CONFIG_MAP]

        @overload
        def __init__(
                self, 
                *, 
                config_map_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointTrustedSigningKeySecret(RegistryEndpointTrustedSigningKey, discriminator='Secret'):
        secret_ref: str
        type: Literal[RegistryEndpointTrustedSigningKeyType.SECRET]

        @overload
        def __init__(
                self, 
                *, 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointTrustedSigningKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIG_MAP = "ConfigMap"
        SECRET = "Secret"


    class azure.mgmt.iotoperations.models.RegistryEndpointUserAssignedIdentityAuthentication(RegistryEndpointAuthentication, discriminator='UserAssignedManagedIdentity'):
        method: Literal[RegistryEndpointAuthenticationMethod.USER_ASSIGNED_MANAGED_IDENTITY]
        user_assigned_managed_identity_settings: RegistryEndpointUserAssignedManagedIdentitySettings

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_managed_identity_settings: RegistryEndpointUserAssignedManagedIdentitySettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.RegistryEndpointUserAssignedManagedIdentitySettings(_Model):
        client_id: str
        scope: Optional[str]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                scope: Optional[str] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.iotoperations.models.ResourceHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEGRADED = "Degraded"
        UNAVAILABLE = "Unavailable"
        UNKNOWN = "Unknown"


    class azure.mgmt.iotoperations.models.ResourceHealthStatus(_Model):
        last_transition_time: Optional[str]
        last_update_time: Optional[str]
        message: Optional[str]
        reason_code: Optional[str]
        status: Optional[Union[str, ResourceHealthState]]


    class azure.mgmt.iotoperations.models.SanForCert(_Model):
        dns: list[str]
        ip: list[str]

        @overload
        def __init__(
                self, 
                *, 
                dns: list[str], 
                ip: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.SchemaRegistryRef(_Model):
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.SecretProviderClassRef(_Model):
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.SelfCheck(_Model):
        interval_seconds: Optional[int]
        mode: Optional[Union[str, OperationalMode]]
        timeout_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                interval_seconds: Optional[int] = ..., 
                mode: Optional[Union[str, OperationalMode]] = ..., 
                timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.SelfTracing(_Model):
        interval_seconds: Optional[int]
        mode: Optional[Union[str, OperationalMode]]

        @overload
        def __init__(
                self, 
                *, 
                interval_seconds: Optional[int] = ..., 
                mode: Optional[Union[str, OperationalMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.ServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER_IP = "ClusterIp"
        LOAD_BALANCER = "LoadBalancer"
        NODE_PORT = "NodePort"


    class azure.mgmt.iotoperations.models.SourceSerializationFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "Json"


    class azure.mgmt.iotoperations.models.StateStoreResourceDefinitionMethods(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ = "Read"
        READ_WRITE = "ReadWrite"
        WRITE = "Write"


    class azure.mgmt.iotoperations.models.StateStoreResourceKeyTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY = "Binary"
        PATTERN = "Pattern"
        STRING = "String"


    class azure.mgmt.iotoperations.models.StateStoreResourceRule(_Model):
        key_type: Union[str, StateStoreResourceKeyTypes]
        keys_property: list[str]
        method: Union[str, StateStoreResourceDefinitionMethods]

        @overload
        def __init__(
                self, 
                *, 
                key_type: Union[str, StateStoreResourceKeyTypes], 
                keys_property: list[str], 
                method: Union[str, StateStoreResourceDefinitionMethods]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.SubscriberMessageDropStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DROP_OLDEST = "DropOldest"
        NONE = "None"


    class azure.mgmt.iotoperations.models.SubscriberQueueLimit(_Model):
        length: Optional[int]
        strategy: Optional[Union[str, SubscriberMessageDropStrategy]]

        @overload
        def __init__(
                self, 
                *, 
                length: Optional[int] = ..., 
                strategy: Optional[Union[str, SubscriberMessageDropStrategy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.SystemData(_Model):
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


    class azure.mgmt.iotoperations.models.TlsCertMethod(_Model):
        cert_manager_certificate_spec: Optional[CertManagerCertificateSpec]
        manual: Optional[X509ManualCertificate]
        mode: Union[str, TlsCertMethodMode]

        @overload
        def __init__(
                self, 
                *, 
                cert_manager_certificate_spec: Optional[CertManagerCertificateSpec] = ..., 
                manual: Optional[X509ManualCertificate] = ..., 
                mode: Union[str, TlsCertMethodMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.TlsCertMethodMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.iotoperations.models.TlsProperties(_Model):
        mode: Optional[Union[str, OperationalMode]]
        trusted_ca_certificate_config_map_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, OperationalMode]] = ..., 
                trusted_ca_certificate_config_map_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.Traces(_Model):
        cache_size_megabytes: Optional[int]
        mode: Optional[Union[str, OperationalMode]]
        self_tracing: Optional[SelfTracing]
        span_channel_capacity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cache_size_megabytes: Optional[int] = ..., 
                mode: Optional[Union[str, OperationalMode]] = ..., 
                self_tracing: Optional[SelfTracing] = ..., 
                span_channel_capacity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.TrackedResource(Resource):
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


    class azure.mgmt.iotoperations.models.TransformationSerializationFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELTA = "Delta"
        JSON = "Json"
        PARQUET = "Parquet"


    class azure.mgmt.iotoperations.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.iotoperations.models.VolumeClaimResourceRequirements(_Model):
        claims: Optional[list[VolumeClaimResourceRequirementsClaims]]
        limits: Optional[dict[str, str]]
        requests: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                claims: Optional[list[VolumeClaimResourceRequirementsClaims]] = ..., 
                limits: Optional[dict[str, str]] = ..., 
                requests: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.VolumeClaimResourceRequirementsClaims(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.VolumeClaimSpec(_Model):
        access_modes: Optional[list[str]]
        data_source: Optional[LocalKubernetesReference]
        data_source_ref: Optional[KubernetesReference]
        resources: Optional[VolumeClaimResourceRequirements]
        selector: Optional[VolumeClaimSpecSelector]
        storage_class_name: Optional[str]
        volume_mode: Optional[str]
        volume_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_modes: Optional[list[str]] = ..., 
                data_source: Optional[LocalKubernetesReference] = ..., 
                data_source_ref: Optional[KubernetesReference] = ..., 
                resources: Optional[VolumeClaimResourceRequirements] = ..., 
                selector: Optional[VolumeClaimSpecSelector] = ..., 
                storage_class_name: Optional[str] = ..., 
                volume_mode: Optional[str] = ..., 
                volume_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.VolumeClaimSpecSelector(_Model):
        match_expressions: Optional[list[VolumeClaimSpecSelectorMatchExpressions]]
        match_labels: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                match_expressions: Optional[list[VolumeClaimSpecSelectorMatchExpressions]] = ..., 
                match_labels: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.VolumeClaimSpecSelectorMatchExpressions(_Model):
        key: str
        operator: Union[str, OperatorValues]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                operator: Union[str, OperatorValues], 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotoperations.models.X509ManualCertificate(_Model):
        secret_ref: str

        @overload
        def __init__(
                self, 
                *, 
                secret_ref: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.iotoperations.operations

    class azure.mgmt.iotoperations.operations.AkriConnectorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                resource: AkriConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriConnectorResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                resource: AkriConnectorResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriConnectorResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriConnectorResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AkriConnectorResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_template(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AkriConnectorResource]: ...


    class azure.mgmt.iotoperations.operations.AkriConnectorTemplateOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                resource: AkriConnectorTemplateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriConnectorTemplateResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                resource: AkriConnectorTemplateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriConnectorTemplateResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriConnectorTemplateResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> AkriConnectorTemplateResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_instance_resource(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AkriConnectorTemplateResource]: ...


    class azure.mgmt.iotoperations.operations.AkriServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                resource: AkriServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                resource: AkriServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AkriServiceResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name']}, api_versions_list=['2026-03-01', '2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name', 'accept']}, api_versions_list=['2026-03-01', '2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> AkriServiceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2026-03-01', '2026-07-01'])
        def list_by_instance_resource(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AkriServiceResource]: ...


    class azure.mgmt.iotoperations.operations.BrokerAuthenticationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                resource: BrokerAuthenticationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerAuthenticationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                resource: BrokerAuthenticationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerAuthenticationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerAuthenticationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authentication_name: str, 
                **kwargs: Any
            ) -> BrokerAuthenticationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BrokerAuthenticationResource]: ...


    class azure.mgmt.iotoperations.operations.BrokerAuthorizationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                resource: BrokerAuthorizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerAuthorizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                resource: BrokerAuthorizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerAuthorizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerAuthorizationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> BrokerAuthorizationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BrokerAuthorizationResource]: ...


    class azure.mgmt.iotoperations.operations.BrokerListenerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                resource: BrokerListenerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerListenerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                resource: BrokerListenerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerListenerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerListenerResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                listener_name: str, 
                **kwargs: Any
            ) -> BrokerListenerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BrokerListenerResource]: ...


    class azure.mgmt.iotoperations.operations.BrokerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                resource: BrokerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                resource: BrokerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BrokerResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                broker_name: str, 
                **kwargs: Any
            ) -> BrokerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BrokerResource]: ...


    class azure.mgmt.iotoperations.operations.DataflowEndpointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                resource: DataflowEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                resource: DataflowEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowEndpointResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_endpoint_name: str, 
                **kwargs: Any
            ) -> DataflowEndpointResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataflowEndpointResource]: ...


    class azure.mgmt.iotoperations.operations.DataflowGraphOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                resource: DataflowGraphResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowGraphResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                resource: DataflowGraphResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowGraphResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowGraphResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> DataflowGraphResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_dataflow_profile(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataflowGraphResource]: ...


    class azure.mgmt.iotoperations.operations.DataflowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                resource: DataflowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                resource: DataflowResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_name: str, 
                **kwargs: Any
            ) -> DataflowResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataflowResource]: ...


    class azure.mgmt.iotoperations.operations.DataflowProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                resource: DataflowProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowProfileResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                resource: DataflowProfileResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowProfileResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataflowProfileResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                **kwargs: Any
            ) -> DataflowProfileResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataflowProfileResource]: ...


    class azure.mgmt.iotoperations.operations.InstanceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                resource: InstanceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InstanceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                resource: InstanceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InstanceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InstanceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> InstanceResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InstanceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[InstanceResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                properties: InstancePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InstanceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                properties: InstancePatchModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InstanceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InstanceResource: ...


    class azure.mgmt.iotoperations.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.iotoperations.operations.RegistryEndpointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                resource: RegistryEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                resource: RegistryEndpointResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryEndpointResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryEndpointResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> RegistryEndpointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01', '2026-07-01'])
        def list_by_instance_resource(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RegistryEndpointResource]: ...


namespace azure.mgmt.iotoperations.types

    class azure.mgmt.iotoperations.types.AdvancedSettings(TypedDict, total=False):
        key "clients": ForwardRef('ClientConfig', module='types')
        key "encryptInternalTraffic": Union[str, OperationalMode]
        key "internalCerts": ForwardRef('CertManagerCertOptions', module='types')
        clients: ClientConfig
        encrypt_internal_traffic: Union[str, OperationalMode]
        internal_certs: CertManagerCertOptions


    class azure.mgmt.iotoperations.types.AkriConnectorAllocatedDevice(TypedDict, total=False):
        key "deviceInboundEndpointName": Required[str]
        key "deviceName": Required[str]
        device_inbound_endpoint_name: str
        device_name: str


    class azure.mgmt.iotoperations.types.AkriConnectorProperties(TypedDict, total=False):
        key "healthState": Union[str, ResourceHealthState]
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('AkriConnectorStatus', module='types')
        allocatedDevices: list[AkriConnectorAllocatedDevice]
        allocated_devices: list[AkriConnectorAllocatedDevice]
        health_state: Union[str, ResourceHealthState]
        provisioning_state: Union[str, ProvisioningState]
        status: AkriConnectorStatus


    class azure.mgmt.iotoperations.types.AkriConnectorResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('AkriConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: AkriConnectorProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.AkriConnectorStatus(TypedDict, total=False):
        key "healthState": ForwardRef('ResourceHealthStatus', module='types')
        health_state: ResourceHealthStatus


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateAioMetadata(TypedDict, total=False):
        key "aioMaxVersion": str
        key "aioMinVersion": str
        aio_max_version: str
        aio_min_version: str


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateAllocation(TypedDict, total=False):
        key "bucketSize": Required[int]
        key "policy": Required[Literal[AkriConnectorTemplateAllocationPolicy.BUCKETIZED]]
        bucket_size: int
        policy: Literal[AkriConnectorTemplateAllocationPolicy.BUCKETIZED]


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateAllocationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUCKETIZED = "Bucketized"


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateBucketizedAllocation(TypedDict, total=False):
        key "bucketSize": Required[int]
        key "policy": Required[Literal[AkriConnectorTemplateAllocationPolicy.BUCKETIZED]]
        bucket_size: int
        policy: Literal[AkriConnectorTemplateAllocationPolicy.BUCKETIZED]


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateDeviceInboundEndpointType(TypedDict, total=False):
        key "displayName": str
        key "endpointType": Required[str]
        key "version": str
        display_name: str
        endpoint_type: str
        version: str


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateDiagnostics(TypedDict, total=False):
        key "logs": Required[AkriConnectorsDiagnosticsLogs]
        logs: AkriConnectorsDiagnosticsLogs


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateExecAction(TypedDict, total=False):
        key "command": Required[list[str]]
        command: list[str]


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateManagedConfiguration(TypedDict, total=False):
        key "managedConfigurationSettings": Required[AkriConnectorTemplateManagedConfigurationSettings]
        key "runtimeConfigurationType": Required[Literal[AkriConnectorTemplateRuntimeConfigurationType.MANAGED_CONFIGURATION]]
        managed_configuration_settings: AkriConnectorTemplateManagedConfigurationSettings
        runtime_configuration_type: Literal[AkriConnectorTemplateRuntimeConfigurationType.MANAGED_CONFIGURATION]


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateManagedConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE_CONFIGURATION = "ImageConfiguration"
        STATEFUL_SET_CONFIGURATION = "StatefulSetConfiguration"


    class azure.mgmt.iotoperations.types.AkriConnectorTemplatePersistentVolumeClaim(TypedDict, total=False):
        key "claimName": Required[str]
        key "mountPath": Required[str]
        claim_name: str
        mount_path: str


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateProperties(TypedDict, total=False):
        key "aioMetadata": ForwardRef('AkriConnectorTemplateAioMetadata', module='types')
        key "connectorMetadataRef": str
        key "deviceInboundEndpointTypes": Required[list[AkriConnectorTemplateDeviceInboundEndpointType]]
        key "diagnostics": ForwardRef('AkriConnectorTemplateDiagnostics', module='types')
        key "healthState": Union[str, ResourceHealthState]
        key "mqttConnectionConfiguration": ForwardRef('AkriConnectorsMqttConnectionConfiguration', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "runtimeConfiguration": Required[AkriConnectorTemplateRuntimeConfiguration]
        aio_metadata: AkriConnectorTemplateAioMetadata
        connector_metadata_ref: str
        device_inbound_endpoint_types: list[AkriConnectorTemplateDeviceInboundEndpointType]
        diagnostics: AkriConnectorTemplateDiagnostics
        health_state: Union[str, ResourceHealthState]
        mqtt_connection_configuration: AkriConnectorsMqttConnectionConfiguration
        provisioning_state: Union[str, ProvisioningState]
        runtime_configuration: AkriConnectorTemplateRuntimeConfiguration


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateReadinessProbe(TypedDict, total=False):
        key "exec": ForwardRef('AkriConnectorTemplateExecAction', module='types')
        key "failureThreshold": int
        key "initialDelaySeconds": int
        key "periodSeconds": int
        key "successThreshold": int
        key "timeoutSeconds": int
        exec_property: AkriConnectorTemplateExecAction
        failure_threshold: int
        initial_delay_seconds: int
        period_seconds: int
        success_threshold: int
        timeout_seconds: int


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('AkriConnectorTemplateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: AkriConnectorTemplateProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateRuntimeConfiguration(TypedDict, total=False):
        key "managedConfigurationSettings": Required[AkriConnectorTemplateManagedConfigurationSettings]
        key "runtimeConfigurationType": Required[Literal[AkriConnectorTemplateRuntimeConfigurationType.MANAGED_CONFIGURATION]]
        managed_configuration_settings: AkriConnectorTemplateManagedConfigurationSettings
        runtime_configuration_type: Literal[AkriConnectorTemplateRuntimeConfigurationType.MANAGED_CONFIGURATION]


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateRuntimeConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_CONFIGURATION = "ManagedConfiguration"


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateRuntimeImageConfiguration(TypedDict, total=False):
        key "allocation": ForwardRef('AkriConnectorTemplateAllocation', module='types')
        key "imageConfigurationSettings": Required[AkriConnectorTemplateRuntimeImageConfigurationSettings]
        key "managedConfigurationType": Required[Literal[AkriConnectorTemplateManagedConfigurationType.IMAGE_CONFIGURATION]]
        key "trustSettings": ForwardRef('AkriConnectorTemplateTrustList', module='types')
        additionalConfiguration: dict[str, str]
        additional_configuration: dict[str, str]
        allocation: AkriConnectorTemplateAllocation
        image_configuration_settings: AkriConnectorTemplateRuntimeImageConfigurationSettings
        managed_configuration_type: Literal[AkriConnectorTemplateManagedConfigurationType.IMAGE_CONFIGURATION]
        persistentVolumeClaimTemplates: list[dict[str, Any]]
        persistentVolumeClaims: list[AkriConnectorTemplatePersistentVolumeClaim]
        persistent_volume_claim_templates: list[dict[str, Any]]
        persistent_volume_claims: list[AkriConnectorTemplatePersistentVolumeClaim]
        secrets: list[AkriConnectorsSecret]
        trust_settings: AkriConnectorTemplateTrustList


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateRuntimeImageConfigurationSettings(TypedDict, total=False):
        key "imageName": Required[str]
        key "imagePullPolicy": Union[str, AkriConnectorsImagePullPolicy]
        key "readinessProbe": ForwardRef('AkriConnectorTemplateReadinessProbe', module='types')
        key "registrySettings": ForwardRef('AkriConnectorsRegistrySettings', module='types')
        key "replicas": int
        key "tagDigestSettings": ForwardRef('AkriConnectorsTagDigestSettings', module='types')
        image_name: str
        image_pull_policy: Union[str, AkriConnectorsImagePullPolicy]
        readiness_probe: AkriConnectorTemplateReadinessProbe
        registry_settings: AkriConnectorsRegistrySettings
        replicas: int
        tag_digest_settings: AkriConnectorsTagDigestSettings


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateRuntimeStatefulSetConfiguration(TypedDict, total=False):
        key "allocation": ForwardRef('AkriConnectorTemplateAllocation', module='types')
        key "managedConfigurationType": Required[Literal[AkriConnectorTemplateManagedConfigurationType.STATEFUL_SET_CONFIGURATION]]
        key "statefulSetConfigurationSettings": Required[dict[str, Any]]
        key "trustSettings": ForwardRef('AkriConnectorTemplateTrustList', module='types')
        additionalConfiguration: dict[str, str]
        additional_configuration: dict[str, str]
        allocation: AkriConnectorTemplateAllocation
        managed_configuration_type: Literal[AkriConnectorTemplateManagedConfigurationType.STATEFUL_SET_CONFIGURATION]
        persistentVolumeClaimTemplates: list[dict[str, Any]]
        persistentVolumeClaims: list[AkriConnectorTemplatePersistentVolumeClaim]
        persistent_volume_claim_templates: list[dict[str, Any]]
        persistent_volume_claims: list[AkriConnectorTemplatePersistentVolumeClaim]
        secrets: list[AkriConnectorsSecret]
        stateful_set_configuration_settings: dict[str, Any]
        trust_settings: AkriConnectorTemplateTrustList


    class azure.mgmt.iotoperations.types.AkriConnectorTemplateTrustList(TypedDict, total=False):
        key "trustListSecretRef": Required[str]
        trust_list_secret_ref: str


    class azure.mgmt.iotoperations.types.AkriConnectorsContainerRegistry(TypedDict, total=False):
        key "containerRegistrySettings": Required[AkriConnectorsContainerRegistrySettings]
        key "registrySettingsType": Required[Literal[AkriConnectorsRegistrySettingsType.CONTAINER_REGISTRY]]
        container_registry_settings: AkriConnectorsContainerRegistrySettings
        registry_settings_type: Literal[AkriConnectorsRegistrySettingsType.CONTAINER_REGISTRY]


    class azure.mgmt.iotoperations.types.AkriConnectorsContainerRegistrySettings(TypedDict, total=False):
        key "registry": Required[str]
        imagePullSecrets: list[AkriConnectorsImagePullSecret]
        image_pull_secrets: list[AkriConnectorsImagePullSecret]
        registry: str


    class azure.mgmt.iotoperations.types.AkriConnectorsDiagnosticsLogs(TypedDict, total=False):
        key "level": str
        level: str


    class azure.mgmt.iotoperations.types.AkriConnectorsDigest(TypedDict, total=False):
        key "digest": Required[str]
        key "tagDigestType": Required[Literal[AkriConnectorsTagDigestType.DIGEST]]
        digest: str
        tag_digest_type: Literal[AkriConnectorsTagDigestType.DIGEST]


    class azure.mgmt.iotoperations.types.AkriConnectorsImagePullSecret(TypedDict, total=False):
        key "secretRef": Required[str]
        secret_ref: str


    class azure.mgmt.iotoperations.types.AkriConnectorsMqttAuthentication(TypedDict, total=False):
        key "method": Required[Literal[AkriConnectorsMqttAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]]
        key "serviceAccountTokenSettings": Required[AkriConnectorsServiceAccountTokenSettings]
        method: Literal[AkriConnectorsMqttAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]
        service_account_token_settings: AkriConnectorsServiceAccountTokenSettings


    class azure.mgmt.iotoperations.types.AkriConnectorsMqttAuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_ACCOUNT_TOKEN = "ServiceAccountToken"


    class azure.mgmt.iotoperations.types.AkriConnectorsMqttConnectionConfiguration(TypedDict, total=False):
        key "authentication": ForwardRef('AkriConnectorsMqttAuthentication', module='types')
        key "host": str
        key "keepAliveSeconds": int
        key "maxInflightMessages": int
        key "protocol": Union[str, AkriConnectorsMqttProtocolType]
        key "sessionExpirySeconds": int
        key "tls": ForwardRef('TlsProperties', module='types')
        authentication: AkriConnectorsMqttAuthentication
        host: str
        keep_alive_seconds: int
        max_inflight_messages: int
        protocol: Union[str, AkriConnectorsMqttProtocolType]
        session_expiry_seconds: int
        tls: TlsProperties


    class azure.mgmt.iotoperations.types.AkriConnectorsRegistryEndpointRef(TypedDict, total=False):
        key "registryEndpointRef": Required[str]
        key "registrySettingsType": Required[Literal[AkriConnectorsRegistrySettingsType.REGISTRY_ENDPOINT_REF]]
        registry_endpoint_ref: str
        registry_settings_type: Literal[AkriConnectorsRegistrySettingsType.REGISTRY_ENDPOINT_REF]


    class azure.mgmt.iotoperations.types.AkriConnectorsRegistrySettingsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_REGISTRY = "ContainerRegistry"
        REGISTRY_ENDPOINT_REF = "RegistryEndpointRef"


    class azure.mgmt.iotoperations.types.AkriConnectorsSecret(TypedDict, total=False):
        key "secretAlias": Required[str]
        key "secretKey": Required[str]
        key "secretRef": Required[str]
        secret_alias: str
        secret_key: str
        secret_ref: str


    class azure.mgmt.iotoperations.types.AkriConnectorsServiceAccountAuthentication(TypedDict, total=False):
        key "method": Required[Literal[AkriConnectorsMqttAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]]
        key "serviceAccountTokenSettings": Required[AkriConnectorsServiceAccountTokenSettings]
        method: Literal[AkriConnectorsMqttAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]
        service_account_token_settings: AkriConnectorsServiceAccountTokenSettings


    class azure.mgmt.iotoperations.types.AkriConnectorsServiceAccountTokenSettings(TypedDict, total=False):
        key "audience": Required[str]
        audience: str


    class azure.mgmt.iotoperations.types.AkriConnectorsTag(TypedDict, total=False):
        key "tag": Required[str]
        key "tagDigestType": Required[Literal[AkriConnectorsTagDigestType.TAG]]
        tag: str
        tag_digest_type: Literal[AkriConnectorsTagDigestType.TAG]


    class azure.mgmt.iotoperations.types.AkriConnectorsTagDigestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIGEST = "Digest"
        TAG = "Tag"


    class azure.mgmt.iotoperations.types.AkriServiceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('AkriServiceStatus', module='types')
        provisioning_state: Union[str, ProvisioningState]
        status: AkriServiceStatus


    class azure.mgmt.iotoperations.types.AkriServiceResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('AkriServiceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: AkriServiceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.AkriServiceStatus(TypedDict, total=False):
        key "healthState": ForwardRef('ResourceHealthStatus', module='types')
        health_state: ResourceHealthStatus


    class azure.mgmt.iotoperations.types.AuthorizationConfig(TypedDict, total=False):
        key "cache": Union[str, OperationalMode]
        cache: Union[str, OperationalMode]
        rules: list[AuthorizationRule]


    class azure.mgmt.iotoperations.types.AuthorizationRule(TypedDict, total=False):
        key "brokerResources": Required[list[BrokerResourceRule]]
        key "principals": Required[PrincipalDefinition]
        broker_resources: list[BrokerResourceRule]
        principals: PrincipalDefinition
        stateStoreResources: list[StateStoreResourceRule]
        state_store_resources: list[StateStoreResourceRule]


    class azure.mgmt.iotoperations.types.AzureDeviceRegistryNamespaceRef(TypedDict, total=False):
        key "resourceId": Required[str]
        resource_id: str


    class azure.mgmt.iotoperations.types.BackendChain(TypedDict, total=False):
        key "partitions": Required[int]
        key "redundancyFactor": Required[int]
        key "workers": int
        partitions: int
        redundancy_factor: int
        workers: int


    class azure.mgmt.iotoperations.types.BatchingConfiguration(TypedDict, total=False):
        key "latencySeconds": int
        key "maxMessages": int
        latency_seconds: int
        max_messages: int


    class azure.mgmt.iotoperations.types.BrokerAuthenticationProperties(TypedDict, total=False):
        key "authenticationMethods": Required[list[BrokerAuthenticatorMethods]]
        key "healthState": Union[str, ResourceHealthState]
        key "provisioningState": Union[str, ProvisioningState]
        authentication_methods: list[BrokerAuthenticatorMethods]
        health_state: Union[str, ResourceHealthState]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.iotoperations.types.BrokerAuthenticationResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('BrokerAuthenticationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: BrokerAuthenticationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.BrokerAuthenticatorCustomAuth(TypedDict, total=False):
        key "x509": Required[X509ManualCertificate]
        x509: X509ManualCertificate


    class azure.mgmt.iotoperations.types.BrokerAuthenticatorMethodCustom(TypedDict, total=False):
        key "auth": ForwardRef('BrokerAuthenticatorCustomAuth', module='types')
        key "caCertConfigMap": str
        key "endpoint": Required[str]
        auth: BrokerAuthenticatorCustomAuth
        ca_cert_config_map: str
        endpoint: str
        headers: dict[str, str]


    class azure.mgmt.iotoperations.types.BrokerAuthenticatorMethodSat(TypedDict, total=False):
        key "audiences": Required[list[str]]
        audiences: list[str]


    class azure.mgmt.iotoperations.types.BrokerAuthenticatorMethodX509(TypedDict, total=False):
        key "additionalValidation": Union[str, BrokerAuthenticatorValidationMethods]
        key "trustedClientCaCert": str
        additional_validation: Union[str, BrokerAuthenticatorValidationMethods]
        authorizationAttributes: dict[str, BrokerAuthenticatorMethodX509Attributes]
        authorization_attributes: dict[str, BrokerAuthenticatorMethodX509Attributes]
        trusted_client_ca_cert: str


    class azure.mgmt.iotoperations.types.BrokerAuthenticatorMethodX509Attributes(TypedDict, total=False):
        key "attributes": Required[dict[str, str]]
        key "subject": Required[str]
        attributes: dict[str, str]
        subject: str


    class azure.mgmt.iotoperations.types.BrokerAuthenticatorMethods(TypedDict, total=False):
        key "customSettings": ForwardRef('BrokerAuthenticatorMethodCustom', module='types')
        key "method": Required[Union[str, BrokerAuthenticationMethod]]
        key "serviceAccountTokenSettings": ForwardRef('BrokerAuthenticatorMethodSat', module='types')
        key "x509Settings": ForwardRef('BrokerAuthenticatorMethodX509', module='types')
        custom_settings: BrokerAuthenticatorMethodCustom
        method: Union[str, BrokerAuthenticationMethod]
        service_account_token_settings: BrokerAuthenticatorMethodSat
        x509_settings: BrokerAuthenticatorMethodX509


    class azure.mgmt.iotoperations.types.BrokerAuthorizationProperties(TypedDict, total=False):
        key "authorizationPolicies": Required[AuthorizationConfig]
        key "healthState": Union[str, ResourceHealthState]
        key "provisioningState": Union[str, ProvisioningState]
        authorization_policies: AuthorizationConfig
        health_state: Union[str, ResourceHealthState]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.iotoperations.types.BrokerAuthorizationResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('BrokerAuthorizationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: BrokerAuthorizationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.BrokerDiagnostics(TypedDict, total=False):
        key "logs": ForwardRef('DiagnosticsLogs', module='types')
        key "metrics": ForwardRef('Metrics', module='types')
        key "selfCheck": ForwardRef('SelfCheck', module='types')
        key "traces": ForwardRef('Traces', module='types')
        logs: DiagnosticsLogs
        metrics: Metrics
        self_check: SelfCheck
        traces: Traces


    class azure.mgmt.iotoperations.types.BrokerListenerProperties(TypedDict, total=False):
        key "healthState": Union[str, ResourceHealthState]
        key "ports": Required[list[ListenerPort]]
        key "provisioningState": Union[str, ProvisioningState]
        key "serviceName": str
        key "serviceType": Union[str, ServiceType]
        health_state: Union[str, ResourceHealthState]
        ports: list[ListenerPort]
        provisioning_state: Union[str, ProvisioningState]
        service_name: str
        service_type: Union[str, ServiceType]


    class azure.mgmt.iotoperations.types.BrokerListenerResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('BrokerListenerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: BrokerListenerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.BrokerPersistence(TypedDict, total=False):
        key "encryption": ForwardRef('BrokerPersistenceEncryption', module='types')
        key "maxSize": Required[str]
        key "persistentVolumeClaimSpec": ForwardRef('VolumeClaimSpec', module='types')
        key "retain": ForwardRef('BrokerRetainMessagesPolicy', module='types')
        key "stateStore": ForwardRef('BrokerStateStorePolicy', module='types')
        key "subscriberQueue": ForwardRef('BrokerSubscriberQueuePolicy', module='types')
        encryption: BrokerPersistenceEncryption
        max_size: str
        persistent_volume_claim_spec: VolumeClaimSpec
        retain: BrokerRetainMessagesPolicy
        state_store: BrokerStateStorePolicy
        subscriber_queue: BrokerSubscriberQueuePolicy


    class azure.mgmt.iotoperations.types.BrokerPersistenceEncryption(TypedDict, total=False):
        key "mode": Required[Union[str, OperationalMode]]
        mode: Union[str, OperationalMode]


    class azure.mgmt.iotoperations.types.BrokerPersistencePolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CUSTOM = "Custom"
        NONE = "None"


    class azure.mgmt.iotoperations.types.BrokerProperties(TypedDict, total=False):
        key "advanced": ForwardRef('AdvancedSettings', module='types')
        key "cardinality": ForwardRef('Cardinality', module='types')
        key "diagnostics": ForwardRef('BrokerDiagnostics', module='types')
        key "diskBackedMessageBuffer": ForwardRef('DiskBackedMessageBuffer', module='types')
        key "generateResourceLimits": ForwardRef('GenerateResourceLimits', module='types')
        key "healthState": Union[str, ResourceHealthState]
        key "highPriorityMessagesBackpressureHandling": Union[str, HighPriorityMessagesBackpressureHandling]
        key "memoryProfile": Union[str, BrokerMemoryProfile]
        key "persistence": ForwardRef('BrokerPersistence', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('BrokerStatus', module='types')
        advanced: AdvancedSettings
        cardinality: Cardinality
        diagnostics: BrokerDiagnostics
        disk_backed_message_buffer: DiskBackedMessageBuffer
        generate_resource_limits: GenerateResourceLimits
        health_state: Union[str, ResourceHealthState]
        high_priority_messages_backpressure_handling: Union[str, HighPriorityMessagesBackpressureHandling]
        memory_profile: Union[str, BrokerMemoryProfile]
        persistence: BrokerPersistence
        provisioning_state: Union[str, ProvisioningState]
        status: BrokerStatus


    class azure.mgmt.iotoperations.types.BrokerResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('BrokerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: BrokerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.BrokerResourceRule(TypedDict, total=False):
        key "method": Required[Union[str, BrokerResourceDefinitionMethods]]
        clientIds: list[str]
        client_ids: list[str]
        method: Union[str, BrokerResourceDefinitionMethods]
        topics: list[str]


    class azure.mgmt.iotoperations.types.BrokerRetainMessagesCustomPolicy(TypedDict, total=False):
        key "mode": Required[Literal[BrokerPersistencePolicyMode.CUSTOM]]
        key "retainSettings": Required[BrokerRetainMessagesSettings]
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        retain_settings: BrokerRetainMessagesSettings


    class azure.mgmt.iotoperations.types.BrokerRetainMessagesDynamic(TypedDict, total=False):
        key "mode": Required[Union[str, OperationalMode]]
        mode: Union[str, OperationalMode]


    class azure.mgmt.iotoperations.types.BrokerRetainMessagesPolicy(TypedDict, total=False):
        key "mode": Required[Literal[BrokerPersistencePolicyMode.CUSTOM]]
        key "retainSettings": Required[BrokerRetainMessagesSettings]
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        retain_settings: BrokerRetainMessagesSettings


    class azure.mgmt.iotoperations.types.BrokerRetainMessagesSettings(TypedDict, total=False):
        key "dynamic": ForwardRef('BrokerRetainMessagesDynamic', module='types')
        dynamic: BrokerRetainMessagesDynamic
        topics: list[str]


    class azure.mgmt.iotoperations.types.BrokerStateStoreCustomPolicy(TypedDict, total=False):
        key "mode": Required[Literal[BrokerPersistencePolicyMode.CUSTOM]]
        key "stateStoreSettings": Required[BrokerStateStorePolicySettings]
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        state_store_settings: BrokerStateStorePolicySettings


    class azure.mgmt.iotoperations.types.BrokerStateStoreDynamic(TypedDict, total=False):
        key "mode": Required[Union[str, OperationalMode]]
        mode: Union[str, OperationalMode]


    class azure.mgmt.iotoperations.types.BrokerStateStorePolicy(TypedDict, total=False):
        key "mode": Required[Literal[BrokerPersistencePolicyMode.CUSTOM]]
        key "stateStoreSettings": Required[BrokerStateStorePolicySettings]
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        state_store_settings: BrokerStateStorePolicySettings


    class azure.mgmt.iotoperations.types.BrokerStateStorePolicyResources(TypedDict, total=False):
        key "keyType": Required[Union[str, BrokerStateStoreKeyType]]
        key "keys": Required[list[str]]
        key_type: Union[str, BrokerStateStoreKeyType]
        keys_property: list[str]


    class azure.mgmt.iotoperations.types.BrokerStateStorePolicySettings(TypedDict, total=False):
        key "dynamic": ForwardRef('BrokerStateStoreDynamic', module='types')
        dynamic: BrokerStateStoreDynamic
        stateStoreResources: list[BrokerStateStorePolicyResources]
        state_store_resources: list[BrokerStateStorePolicyResources]


    class azure.mgmt.iotoperations.types.BrokerStatus(TypedDict, total=False):
        key "healthState": ForwardRef('ResourceHealthStatus', module='types')
        health_state: ResourceHealthStatus


    class azure.mgmt.iotoperations.types.BrokerSubscriberQueueCustomPolicy(TypedDict, total=False):
        key "mode": Required[Literal[BrokerPersistencePolicyMode.CUSTOM]]
        key "subscriberQueueSettings": Required[BrokerSubscriberQueueCustomPolicySettings]
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        subscriber_queue_settings: BrokerSubscriberQueueCustomPolicySettings


    class azure.mgmt.iotoperations.types.BrokerSubscriberQueueCustomPolicySettings(TypedDict, total=False):
        key "dynamic": ForwardRef('BrokerSubscriberQueueDynamic', module='types')
        dynamic: BrokerSubscriberQueueDynamic
        subscriberClientIds: list[str]
        subscriber_client_ids: list[str]


    class azure.mgmt.iotoperations.types.BrokerSubscriberQueueDynamic(TypedDict, total=False):
        key "mode": Required[Union[str, OperationalMode]]
        mode: Union[str, OperationalMode]


    class azure.mgmt.iotoperations.types.BrokerSubscriberQueuePolicy(TypedDict, total=False):
        key "mode": Required[Literal[BrokerPersistencePolicyMode.CUSTOM]]
        key "subscriberQueueSettings": Required[BrokerSubscriberQueueCustomPolicySettings]
        mode: Literal[BrokerPersistencePolicyMode.CUSTOM]
        subscriber_queue_settings: BrokerSubscriberQueueCustomPolicySettings


    class azure.mgmt.iotoperations.types.Cardinality(TypedDict, total=False):
        key "backendChain": Required[BackendChain]
        key "frontend": Required[Frontend]
        backend_chain: BackendChain
        frontend: Frontend


    class azure.mgmt.iotoperations.types.CertManagerCertOptions(TypedDict, total=False):
        key "duration": Required[str]
        key "privateKey": Required[CertManagerPrivateKey]
        key "renewBefore": Required[str]
        duration: str
        private_key: CertManagerPrivateKey
        renew_before: str


    class azure.mgmt.iotoperations.types.CertManagerCertificateSpec(TypedDict, total=False):
        key "duration": str
        key "issuerRef": Required[CertManagerIssuerRef]
        key "privateKey": ForwardRef('CertManagerPrivateKey', module='types')
        key "renewBefore": str
        key "san": ForwardRef('SanForCert', module='types')
        key "secretName": str
        duration: str
        issuer_ref: CertManagerIssuerRef
        private_key: CertManagerPrivateKey
        renew_before: str
        san: SanForCert
        secret_name: str


    class azure.mgmt.iotoperations.types.CertManagerIssuerRef(TypedDict, total=False):
        key "group": Required[str]
        key "kind": Required[Union[str, CertManagerIssuerKind]]
        key "name": Required[str]
        group: str
        kind: Union[str, CertManagerIssuerKind]
        name: str


    class azure.mgmt.iotoperations.types.CertManagerPrivateKey(TypedDict, total=False):
        key "algorithm": Required[Union[str, PrivateKeyAlgorithm]]
        key "rotationPolicy": Required[Union[str, PrivateKeyRotationPolicy]]
        algorithm: Union[str, PrivateKeyAlgorithm]
        rotation_policy: Union[str, PrivateKeyRotationPolicy]


    class azure.mgmt.iotoperations.types.ClientConfig(TypedDict, total=False):
        key "maxKeepAliveSeconds": int
        key "maxMessageExpirySeconds": int
        key "maxPacketSizeBytes": int
        key "maxReceiveMaximum": int
        key "maxSessionExpirySeconds": int
        key "subscriberQueueLimit": ForwardRef('SubscriberQueueLimit', module='types')
        max_keep_alive_seconds: int
        max_message_expiry_seconds: int
        max_packet_size_bytes: int
        max_receive_maximum: int
        max_session_expiry_seconds: int
        subscriber_queue_limit: SubscriberQueueLimit


    class azure.mgmt.iotoperations.types.DataflowBuiltInTransformationDataset(TypedDict, total=False):
        key "description": str
        key "expression": str
        key "inputs": Required[list[str]]
        key "key": Required[str]
        key "schemaRef": str
        description: str
        expression: str
        inputs: list[str]
        key: str
        schema_ref: str


    class azure.mgmt.iotoperations.types.DataflowBuiltInTransformationFilter(TypedDict, total=False):
        key "description": str
        key "expression": Required[str]
        key "inputs": Required[list[str]]
        key "type": Union[str, FilterType]
        description: str
        expression: str
        inputs: list[str]
        type: Union[str, FilterType]


    class azure.mgmt.iotoperations.types.DataflowBuiltInTransformationMap(TypedDict, total=False):
        key "description": str
        key "expression": str
        key "inputs": Required[list[str]]
        key "output": Required[str]
        key "type": Union[str, DataflowMappingType]
        description: str
        expression: str
        inputs: list[str]
        output: str
        type: Union[str, DataflowMappingType]


    class azure.mgmt.iotoperations.types.DataflowBuiltInTransformationSettings(TypedDict, total=False):
        key "schemaRef": str
        key "serializationFormat": Union[str, TransformationSerializationFormat]
        datasets: list[DataflowBuiltInTransformationDataset]
        filter: list[DataflowBuiltInTransformationFilter]
        map: list[DataflowBuiltInTransformationMap]
        schema_ref: str
        serialization_format: Union[str, TransformationSerializationFormat]


    class azure.mgmt.iotoperations.types.DataflowDestinationAddIfNotPresentHeaderAction(TypedDict, total=False):
        key "actionType": Required[Literal[DataflowHeaderActionType.ADD_IF_NOT_PRESENT]]
        key "key": Required[str]
        key "value": Required[str]
        action_type: Literal[DataflowHeaderActionType.ADD_IF_NOT_PRESENT]
        key: str
        value: str


    class azure.mgmt.iotoperations.types.DataflowDestinationAddOrReplaceHeaderAction(TypedDict, total=False):
        key "actionType": Required[Literal[DataflowHeaderActionType.ADD_OR_REPLACE]]
        key "key": Required[str]
        key "value": Required[str]
        action_type: Literal[DataflowHeaderActionType.ADD_OR_REPLACE]
        key: str
        value: str


    class azure.mgmt.iotoperations.types.DataflowDestinationOperationSettings(TypedDict, total=False):
        key "dataDestination": Required[str]
        key "endpointRef": Required[str]
        data_destination: str
        endpoint_ref: str
        headers: list[DataflowDestinationHeaderAction]


    class azure.mgmt.iotoperations.types.DataflowDestinationRemoveHeaderAction(TypedDict, total=False):
        key "actionType": Required[Literal[DataflowHeaderActionType.REMOVE]]
        key "key": Required[str]
        action_type: Literal[DataflowHeaderActionType.REMOVE]
        key: str


    class azure.mgmt.iotoperations.types.DataflowEndpointAuthenticationAccessToken(TypedDict, total=False):
        key "secretRef": Required[str]
        secret_ref: str


    class azure.mgmt.iotoperations.types.DataflowEndpointAuthenticationAnonymous(TypedDict, total=False):


    class azure.mgmt.iotoperations.types.DataflowEndpointAuthenticationSasl(TypedDict, total=False):
        key "saslType": Required[Union[str, DataflowEndpointAuthenticationSaslType]]
        key "secretRef": Required[str]
        sasl_type: Union[str, DataflowEndpointAuthenticationSaslType]
        secret_ref: str


    class azure.mgmt.iotoperations.types.DataflowEndpointAuthenticationServiceAccountToken(TypedDict, total=False):
        key "audience": Required[str]
        audience: str


    class azure.mgmt.iotoperations.types.DataflowEndpointAuthenticationSystemAssignedManagedIdentity(TypedDict, total=False):
        key "audience": str
        audience: str


    class azure.mgmt.iotoperations.types.DataflowEndpointAuthenticationUserAssignedManagedIdentity(TypedDict, total=False):
        key "clientId": Required[str]
        key "scope": str
        key "tenantId": Required[str]
        client_id: str
        scope: str
        tenant_id: str


    class azure.mgmt.iotoperations.types.DataflowEndpointAuthenticationX509(TypedDict, total=False):
        key "secretRef": Required[str]
        secret_ref: str


    class azure.mgmt.iotoperations.types.DataflowEndpointDataExplorer(TypedDict, total=False):
        key "authentication": Required[DataflowEndpointDataExplorerAuthentication]
        key "batching": ForwardRef('BatchingConfiguration', module='types')
        key "database": Required[str]
        key "host": Required[str]
        authentication: DataflowEndpointDataExplorerAuthentication
        batching: BatchingConfiguration
        database: str
        host: str


    class azure.mgmt.iotoperations.types.DataflowEndpointDataExplorerAuthentication(TypedDict, total=False):
        key "method": Required[Union[str, DataExplorerAuthMethod]]
        key "systemAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationSystemAssignedManagedIdentity', module='types')
        key "userAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationUserAssignedManagedIdentity', module='types')
        method: Union[str, DataExplorerAuthMethod]
        system_assigned_managed_identity_settings: DataflowEndpointAuthenticationSystemAssignedManagedIdentity
        user_assigned_managed_identity_settings: DataflowEndpointAuthenticationUserAssignedManagedIdentity


    class azure.mgmt.iotoperations.types.DataflowEndpointDataLakeStorage(TypedDict, total=False):
        key "authentication": Required[DataflowEndpointDataLakeStorageAuthentication]
        key "batching": ForwardRef('BatchingConfiguration', module='types')
        key "host": Required[str]
        authentication: DataflowEndpointDataLakeStorageAuthentication
        batching: BatchingConfiguration
        host: str


    class azure.mgmt.iotoperations.types.DataflowEndpointDataLakeStorageAuthentication(TypedDict, total=False):
        key "accessTokenSettings": ForwardRef('DataflowEndpointAuthenticationAccessToken', module='types')
        key "method": Required[Union[str, DataLakeStorageAuthMethod]]
        key "systemAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationSystemAssignedManagedIdentity', module='types')
        key "userAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationUserAssignedManagedIdentity', module='types')
        access_token_settings: DataflowEndpointAuthenticationAccessToken
        method: Union[str, DataLakeStorageAuthMethod]
        system_assigned_managed_identity_settings: DataflowEndpointAuthenticationSystemAssignedManagedIdentity
        user_assigned_managed_identity_settings: DataflowEndpointAuthenticationUserAssignedManagedIdentity


    class azure.mgmt.iotoperations.types.DataflowEndpointFabricOneLake(TypedDict, total=False):
        key "authentication": Required[DataflowEndpointFabricOneLakeAuthentication]
        key "batching": ForwardRef('BatchingConfiguration', module='types')
        key "host": Required[str]
        key "names": Required[DataflowEndpointFabricOneLakeNames]
        key "oneLakePathType": Required[Union[str, DataflowEndpointFabricPathType]]
        authentication: DataflowEndpointFabricOneLakeAuthentication
        batching: BatchingConfiguration
        host: str
        names: DataflowEndpointFabricOneLakeNames
        one_lake_path_type: Union[str, DataflowEndpointFabricPathType]


    class azure.mgmt.iotoperations.types.DataflowEndpointFabricOneLakeAuthentication(TypedDict, total=False):
        key "method": Required[Union[str, FabricOneLakeAuthMethod]]
        key "systemAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationSystemAssignedManagedIdentity', module='types')
        key "userAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationUserAssignedManagedIdentity', module='types')
        method: Union[str, FabricOneLakeAuthMethod]
        system_assigned_managed_identity_settings: DataflowEndpointAuthenticationSystemAssignedManagedIdentity
        user_assigned_managed_identity_settings: DataflowEndpointAuthenticationUserAssignedManagedIdentity


    class azure.mgmt.iotoperations.types.DataflowEndpointFabricOneLakeNames(TypedDict, total=False):
        key "lakehouseName": Required[str]
        key "workspaceName": Required[str]
        lakehouse_name: str
        workspace_name: str


    class azure.mgmt.iotoperations.types.DataflowEndpointKafka(TypedDict, total=False):
        key "authentication": Required[DataflowEndpointKafkaAuthentication]
        key "batching": ForwardRef('DataflowEndpointKafkaBatching', module='types')
        key "cloudEventAttributes": Union[str, CloudEventAttributeType]
        key "compression": Union[str, DataflowEndpointKafkaCompression]
        key "consumerGroupId": str
        key "copyMqttProperties": Union[str, OperationalMode]
        key "host": Required[str]
        key "kafkaAcks": Union[str, DataflowEndpointKafkaAcks]
        key "partitionStrategy": Union[str, DataflowEndpointKafkaPartitionStrategy]
        key "tls": ForwardRef('TlsProperties', module='types')
        authentication: DataflowEndpointKafkaAuthentication
        batching: DataflowEndpointKafkaBatching
        cloud_event_attributes: Union[str, CloudEventAttributeType]
        compression: Union[str, DataflowEndpointKafkaCompression]
        consumer_group_id: str
        copy_mqtt_properties: Union[str, OperationalMode]
        host: str
        kafka_acks: Union[str, DataflowEndpointKafkaAcks]
        partition_strategy: Union[str, DataflowEndpointKafkaPartitionStrategy]
        tls: TlsProperties


    class azure.mgmt.iotoperations.types.DataflowEndpointKafkaAuthentication(TypedDict, total=False):
        key "method": Required[Union[str, KafkaAuthMethod]]
        key "saslSettings": ForwardRef('DataflowEndpointAuthenticationSasl', module='types')
        key "systemAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationSystemAssignedManagedIdentity', module='types')
        key "userAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationUserAssignedManagedIdentity', module='types')
        key "x509CertificateSettings": ForwardRef('DataflowEndpointAuthenticationX509', module='types')
        method: Union[str, KafkaAuthMethod]
        sasl_settings: DataflowEndpointAuthenticationSasl
        system_assigned_managed_identity_settings: DataflowEndpointAuthenticationSystemAssignedManagedIdentity
        user_assigned_managed_identity_settings: DataflowEndpointAuthenticationUserAssignedManagedIdentity
        x509_certificate_settings: DataflowEndpointAuthenticationX509


    class azure.mgmt.iotoperations.types.DataflowEndpointKafkaBatching(TypedDict, total=False):
        key "latencyMs": int
        key "maxBytes": int
        key "maxMessages": int
        key "mode": Union[str, OperationalMode]
        latency_ms: int
        max_bytes: int
        max_messages: int
        mode: Union[str, OperationalMode]


    class azure.mgmt.iotoperations.types.DataflowEndpointLocalStorage(TypedDict, total=False):
        key "persistentVolumeClaimRef": Required[str]
        persistent_volume_claim_ref: str


    class azure.mgmt.iotoperations.types.DataflowEndpointMqtt(TypedDict, total=False):
        key "authentication": Required[DataflowEndpointMqttAuthentication]
        key "clientIdPrefix": str
        key "cloudEventAttributes": Union[str, CloudEventAttributeType]
        key "host": str
        key "keepAliveSeconds": int
        key "maxInflightMessages": int
        key "protocol": Union[str, BrokerProtocolType]
        key "qos": int
        key "retain": Union[str, MqttRetainType]
        key "sessionExpirySeconds": int
        key "tls": ForwardRef('TlsProperties', module='types')
        authentication: DataflowEndpointMqttAuthentication
        client_id_prefix: str
        cloud_event_attributes: Union[str, CloudEventAttributeType]
        host: str
        keep_alive_seconds: int
        max_inflight_messages: int
        protocol: Union[str, BrokerProtocolType]
        qos: int
        retain: Union[str, MqttRetainType]
        session_expiry_seconds: int
        tls: TlsProperties


    class azure.mgmt.iotoperations.types.DataflowEndpointMqttAuthentication(TypedDict, total=False):
        key "method": Required[Union[str, MqttAuthMethod]]
        key "serviceAccountTokenSettings": ForwardRef('DataflowEndpointAuthenticationServiceAccountToken', module='types')
        key "systemAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationSystemAssignedManagedIdentity', module='types')
        key "userAssignedManagedIdentitySettings": ForwardRef('DataflowEndpointAuthenticationUserAssignedManagedIdentity', module='types')
        key "x509CertificateSettings": ForwardRef('DataflowEndpointAuthenticationX509', module='types')
        method: Union[str, MqttAuthMethod]
        service_account_token_settings: DataflowEndpointAuthenticationServiceAccountToken
        system_assigned_managed_identity_settings: DataflowEndpointAuthenticationSystemAssignedManagedIdentity
        user_assigned_managed_identity_settings: DataflowEndpointAuthenticationUserAssignedManagedIdentity
        x509_certificate_settings: DataflowEndpointAuthenticationX509


    class azure.mgmt.iotoperations.types.DataflowEndpointOpenTelemetry(TypedDict, total=False):
        key "authentication": Required[DataflowOpenTelemetryAuthentication]
        key "batching": ForwardRef('BatchingConfiguration', module='types')
        key "host": Required[str]
        key "tls": ForwardRef('TlsProperties', module='types')
        authentication: DataflowOpenTelemetryAuthentication
        batching: BatchingConfiguration
        host: str
        tls: TlsProperties


    class azure.mgmt.iotoperations.types.DataflowEndpointProperties(TypedDict, total=False):
        key "dataExplorerSettings": ForwardRef('DataflowEndpointDataExplorer', module='types')
        key "dataLakeStorageSettings": ForwardRef('DataflowEndpointDataLakeStorage', module='types')
        key "endpointType": Required[Union[str, EndpointType]]
        key "fabricOneLakeSettings": ForwardRef('DataflowEndpointFabricOneLake', module='types')
        key "healthState": Union[str, ResourceHealthState]
        key "hostType": Union[str, DataflowEndpointHostType]
        key "kafkaSettings": ForwardRef('DataflowEndpointKafka', module='types')
        key "localStorageSettings": ForwardRef('DataflowEndpointLocalStorage', module='types')
        key "mqttSettings": ForwardRef('DataflowEndpointMqtt', module='types')
        key "openTelemetrySettings": ForwardRef('DataflowEndpointOpenTelemetry', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        data_explorer_settings: DataflowEndpointDataExplorer
        data_lake_storage_settings: DataflowEndpointDataLakeStorage
        endpoint_type: Union[str, EndpointType]
        fabric_one_lake_settings: DataflowEndpointFabricOneLake
        health_state: Union[str, ResourceHealthState]
        host_type: Union[str, DataflowEndpointHostType]
        kafka_settings: DataflowEndpointKafka
        local_storage_settings: DataflowEndpointLocalStorage
        mqtt_settings: DataflowEndpointMqtt
        open_telemetry_settings: DataflowEndpointOpenTelemetry
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.iotoperations.types.DataflowEndpointResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataflowEndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: DataflowEndpointProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.DataflowGraphConnectionInput(TypedDict, total=False):
        key "name": Required[str]
        key "schema": ForwardRef('DataflowGraphConnectionSchemaSettings', module='types')
        name: str
        schema: DataflowGraphConnectionSchemaSettings


    class azure.mgmt.iotoperations.types.DataflowGraphConnectionOutput(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.iotoperations.types.DataflowGraphConnectionSchemaSettings(TypedDict, total=False):
        key "schemaRef": str
        key "serializationFormat": Union[str, DataflowGraphConnectionSchemaSerializationFormat]
        schema_ref: str
        serialization_format: Union[str, DataflowGraphConnectionSchemaSerializationFormat]


    class azure.mgmt.iotoperations.types.DataflowGraphDestinationAddIfNotPresentHeaderAction(TypedDict, total=False):
        key "actionType": Required[Literal[DataflowGraphDestinationHeaderActionType.ADD_IF_NOT_PRESENT]]
        key "key": Required[str]
        key "value": Required[str]
        action_type: Literal[DataflowGraphDestinationHeaderActionType.ADD_IF_NOT_PRESENT]
        key: str
        value: str


    class azure.mgmt.iotoperations.types.DataflowGraphDestinationAddOrReplaceHeaderAction(TypedDict, total=False):
        key "actionType": Required[Literal[DataflowGraphDestinationHeaderActionType.ADD_OR_REPLACE]]
        key "key": Required[str]
        key "value": Required[str]
        action_type: Literal[DataflowGraphDestinationHeaderActionType.ADD_OR_REPLACE]
        key: str
        value: str


    class azure.mgmt.iotoperations.types.DataflowGraphDestinationHeaderActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_IF_NOT_PRESENT = "AddIfNotPresent"
        ADD_OR_REPLACE = "AddOrReplace"
        REMOVE = "Remove"


    class azure.mgmt.iotoperations.types.DataflowGraphDestinationNode(TypedDict, total=False):
        key "destinationSettings": Required[DataflowGraphDestinationNodeSettings]
        key "name": Required[str]
        key "nodeType": Required[Literal[DataflowGraphNodeType.DESTINATION]]
        destination_settings: DataflowGraphDestinationNodeSettings
        name: str
        node_type: Literal[DataflowGraphNodeType.DESTINATION]


    class azure.mgmt.iotoperations.types.DataflowGraphDestinationNodeSettings(TypedDict, total=False):
        key "dataDestination": Required[str]
        key "endpointRef": Required[str]
        data_destination: str
        endpoint_ref: str
        headers: list[DataflowGraphDestinationHeaderAction]


    class azure.mgmt.iotoperations.types.DataflowGraphDestinationRemoveHeaderAction(TypedDict, total=False):
        key "actionType": Required[Literal[DataflowGraphDestinationHeaderActionType.REMOVE]]
        key "key": Required[str]
        action_type: Literal[DataflowGraphDestinationHeaderActionType.REMOVE]
        key: str


    class azure.mgmt.iotoperations.types.DataflowGraphGraphNode(TypedDict, total=False):
        key "graphSettings": Required[DataflowGraphNodeGraphSettings]
        key "name": Required[str]
        key "nodeType": Required[Literal[DataflowGraphNodeType.GRAPH]]
        graph_settings: DataflowGraphNodeGraphSettings
        name: str
        node_type: Literal[DataflowGraphNodeType.GRAPH]


    class azure.mgmt.iotoperations.types.DataflowGraphGraphNodeConfiguration(TypedDict, total=False):
        key "key": Required[str]
        key "value": Required[str]
        key: str
        value: str


    class azure.mgmt.iotoperations.types.DataflowGraphNodeConnection(TypedDict):
        key "from": Required[DataflowGraphConnectionInput]
        key "to": Required[DataflowGraphConnectionOutput]
        from_property: DataflowGraphConnectionInput
        to: DataflowGraphConnectionOutput


    class azure.mgmt.iotoperations.types.DataflowGraphNodeGraphSettings(TypedDict, total=False):
        key "artifact": Required[str]
        key "registryEndpointRef": Required[str]
        artifact: str
        configuration: list[DataflowGraphGraphNodeConfiguration]
        registry_endpoint_ref: str


    class azure.mgmt.iotoperations.types.DataflowGraphNodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESTINATION = "Destination"
        GRAPH = "Graph"
        SOURCE = "Source"


    class azure.mgmt.iotoperations.types.DataflowGraphProperties(TypedDict, total=False):
        key "healthState": Union[str, ResourceHealthState]
        key "mode": Union[str, OperationalMode]
        key "nodeConnections": Required[list[DataflowGraphNodeConnection]]
        key "nodes": Required[list[DataflowGraphNode]]
        key "provisioningState": Union[str, ProvisioningState]
        key "requestDiskPersistence": Union[str, OperationalMode]
        key "status": ForwardRef('DataflowGraphStatus', module='types')
        health_state: Union[str, ResourceHealthState]
        mode: Union[str, OperationalMode]
        node_connections: list[DataflowGraphNodeConnection]
        nodes: list[DataflowGraphNode]
        provisioning_state: Union[str, ProvisioningState]
        request_disk_persistence: Union[str, OperationalMode]
        status: DataflowGraphStatus


    class azure.mgmt.iotoperations.types.DataflowGraphResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataflowGraphProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: DataflowGraphProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.DataflowGraphSourceNode(TypedDict, total=False):
        key "name": Required[str]
        key "nodeType": Required[Literal[DataflowGraphNodeType.SOURCE]]
        key "sourceSettings": Required[DataflowGraphSourceSettings]
        name: str
        node_type: Literal[DataflowGraphNodeType.SOURCE]
        source_settings: DataflowGraphSourceSettings


    class azure.mgmt.iotoperations.types.DataflowGraphSourceSettings(TypedDict, total=False):
        key "assetRef": str
        key "dataSources": Required[list[str]]
        key "endpointRef": Required[str]
        asset_ref: str
        data_sources: list[str]
        endpoint_ref: str


    class azure.mgmt.iotoperations.types.DataflowGraphStatus(TypedDict, total=False):
        key "healthState": ForwardRef('ResourceHealthStatus', module='types')
        health_state: ResourceHealthStatus


    class azure.mgmt.iotoperations.types.DataflowHeaderActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_IF_NOT_PRESENT = "AddIfNotPresent"
        ADD_OR_REPLACE = "AddOrReplace"
        REMOVE = "Remove"


    class azure.mgmt.iotoperations.types.DataflowOpenTelemetryAnonymousAuthentication(TypedDict, total=False):
        key "anonymousSettings": Required[DataflowEndpointAuthenticationAnonymous]
        key "method": Required[Literal[DataflowOpenTelemetryAuthenticationMethod.ANONYMOUS]]
        anonymous_settings: DataflowEndpointAuthenticationAnonymous
        method: Literal[DataflowOpenTelemetryAuthenticationMethod.ANONYMOUS]


    class azure.mgmt.iotoperations.types.DataflowOpenTelemetryAuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "Anonymous"
        SERVICE_ACCOUNT_TOKEN = "ServiceAccountToken"
        X509_CERTIFICATE = "X509Certificate"


    class azure.mgmt.iotoperations.types.DataflowOpenTelemetryServiceAccountAuthentication(TypedDict, total=False):
        key "method": Required[Literal[DataflowOpenTelemetryAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]]
        key "serviceAccountTokenSettings": Required[DataflowEndpointAuthenticationServiceAccountToken]
        method: Literal[DataflowOpenTelemetryAuthenticationMethod.SERVICE_ACCOUNT_TOKEN]
        service_account_token_settings: DataflowEndpointAuthenticationServiceAccountToken


    class azure.mgmt.iotoperations.types.DataflowOpenTelemetryX509CertificateAuthentication(TypedDict, total=False):
        key "method": Required[Literal[DataflowOpenTelemetryAuthenticationMethod.X509_CERTIFICATE]]
        key "x509CertificateSettings": Required[DataflowEndpointAuthenticationX509]
        method: Literal[DataflowOpenTelemetryAuthenticationMethod.X509_CERTIFICATE]
        x509_certificate_settings: DataflowEndpointAuthenticationX509


    class azure.mgmt.iotoperations.types.DataflowOperation(TypedDict, total=False):
        key "builtInTransformationSettings": ForwardRef('DataflowBuiltInTransformationSettings', module='types')
        key "destinationSettings": ForwardRef('DataflowDestinationOperationSettings', module='types')
        key "name": str
        key "operationType": Required[Union[str, OperationType]]
        key "sourceSettings": ForwardRef('DataflowSourceOperationSettings', module='types')
        built_in_transformation_settings: DataflowBuiltInTransformationSettings
        destination_settings: DataflowDestinationOperationSettings
        name: str
        operation_type: Union[str, OperationType]
        source_settings: DataflowSourceOperationSettings


    class azure.mgmt.iotoperations.types.DataflowProfileProperties(TypedDict, total=False):
        key "diagnostics": ForwardRef('ProfileDiagnostics', module='types')
        key "healthState": Union[str, ResourceHealthState]
        key "instanceCount": int
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('DataflowProfileStatus', module='types')
        diagnostics: ProfileDiagnostics
        health_state: Union[str, ResourceHealthState]
        instance_count: int
        provisioning_state: Union[str, ProvisioningState]
        status: DataflowProfileStatus


    class azure.mgmt.iotoperations.types.DataflowProfileResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataflowProfileProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: DataflowProfileProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.DataflowProfileStatus(TypedDict, total=False):
        key "healthState": ForwardRef('ResourceHealthStatus', module='types')
        health_state: ResourceHealthStatus


    class azure.mgmt.iotoperations.types.DataflowProperties(TypedDict, total=False):
        key "healthState": Union[str, ResourceHealthState]
        key "mode": Union[str, OperationalMode]
        key "operations": Required[list[DataflowOperation]]
        key "provisioningState": Union[str, ProvisioningState]
        key "requestDiskPersistence": Union[str, OperationalMode]
        key "status": ForwardRef('DataflowStatus', module='types')
        health_state: Union[str, ResourceHealthState]
        mode: Union[str, OperationalMode]
        operations: list[DataflowOperation]
        provisioning_state: Union[str, ProvisioningState]
        request_disk_persistence: Union[str, OperationalMode]
        status: DataflowStatus


    class azure.mgmt.iotoperations.types.DataflowResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('DataflowProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: DataflowProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.DataflowSourceOperationSettings(TypedDict, total=False):
        key "assetRef": str
        key "dataSources": Required[list[str]]
        key "endpointRef": Required[str]
        key "schemaRef": str
        key "serializationFormat": Union[str, SourceSerializationFormat]
        asset_ref: str
        data_sources: list[str]
        endpoint_ref: str
        schema_ref: str
        serialization_format: Union[str, SourceSerializationFormat]


    class azure.mgmt.iotoperations.types.DataflowStatus(TypedDict, total=False):
        key "healthState": ForwardRef('ResourceHealthStatus', module='types')
        health_state: ResourceHealthStatus


    class azure.mgmt.iotoperations.types.DiagnosticsLogs(TypedDict, total=False):
        key "level": str
        level: str


    class azure.mgmt.iotoperations.types.DiskBackedMessageBuffer(TypedDict, total=False):
        key "ephemeralVolumeClaimSpec": ForwardRef('VolumeClaimSpec', module='types')
        key "maxSize": Required[str]
        key "persistentVolumeClaimSpec": ForwardRef('VolumeClaimSpec', module='types')
        ephemeral_volume_claim_spec: VolumeClaimSpec
        max_size: str
        persistent_volume_claim_spec: VolumeClaimSpec


    class azure.mgmt.iotoperations.types.ExtendedLocation(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, ExtendedLocationType]]
        name: str
        type: Union[str, ExtendedLocationType]


    class azure.mgmt.iotoperations.types.Frontend(TypedDict, total=False):
        key "replicas": Required[int]
        key "workers": int
        replicas: int
        workers: int


    class azure.mgmt.iotoperations.types.GenerateResourceLimits(TypedDict, total=False):
        key "cpu": Union[str, OperationalMode]
        cpu: Union[str, OperationalMode]


    class azure.mgmt.iotoperations.types.InstanceFeature(TypedDict, total=False):
        key "mode": Union[str, InstanceFeatureMode]
        mode: Union[str, InstanceFeatureMode]
        settings: dict[str, Union[str, OperationalMode]]


    class azure.mgmt.iotoperations.types.InstancePatchModel(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.iotoperations.types.InstanceProperties(TypedDict, total=False):
        key "adrNamespaceRef": ForwardRef('AzureDeviceRegistryNamespaceRef', module='types')
        key "defaultSecretProviderClassRef": ForwardRef('SecretProviderClassRef', module='types')
        key "description": str
        key "healthState": Union[str, ResourceHealthState]
        key "provisioningState": Union[str, ProvisioningState]
        key "schemaRegistryRef": Required[SchemaRegistryRef]
        key "version": str
        adr_namespace_ref: AzureDeviceRegistryNamespaceRef
        default_secret_provider_class_ref: SecretProviderClassRef
        description: str
        features: dict[str, InstanceFeature]
        health_state: Union[str, ResourceHealthState]
        provisioning_state: Union[str, ProvisioningState]
        schema_registry_ref: SchemaRegistryRef
        version: str


    class azure.mgmt.iotoperations.types.InstanceResource(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('InstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: InstanceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.iotoperations.types.KubernetesReference(TypedDict, total=False):
        key "apiGroup": str
        key "kind": Required[str]
        key "name": Required[str]
        key "namespace": str
        api_group: str
        kind: str
        name: str
        namespace: str


    class azure.mgmt.iotoperations.types.ListenerPort(TypedDict, total=False):
        key "authenticationRef": str
        key "authorizationRef": str
        key "nodePort": int
        key "port": Required[int]
        key "protocol": Union[str, BrokerProtocolType]
        key "tls": ForwardRef('TlsCertMethod', module='types')
        authentication_ref: str
        authorization_ref: str
        node_port: int
        port: int
        protocol: Union[str, BrokerProtocolType]
        tls: TlsCertMethod


    class azure.mgmt.iotoperations.types.LocalKubernetesReference(TypedDict, total=False):
        key "apiGroup": str
        key "kind": Required[str]
        key "name": Required[str]
        api_group: str
        kind: str
        name: str


    class azure.mgmt.iotoperations.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.iotoperations.types.Metrics(TypedDict, total=False):
        key "prometheusPort": int
        prometheus_port: int


    class azure.mgmt.iotoperations.types.PrincipalDefinition(TypedDict, total=False):
        attributes: list[dict[str, str]]
        clientIds: list[str]
        client_ids: list[str]
        usernames: list[str]


    class azure.mgmt.iotoperations.types.ProfileDiagnostics(TypedDict, total=False):
        key "logs": ForwardRef('DiagnosticsLogs', module='types')
        key "metrics": ForwardRef('Metrics', module='types')
        logs: DiagnosticsLogs
        metrics: Metrics


    class azure.mgmt.iotoperations.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.RegistryEndpointAnonymousAuthentication(TypedDict, total=False):
        key "anonymousSettings": Required[RegistryEndpointAnonymousSettings]
        key "method": Required[Literal[RegistryEndpointAuthenticationMethod.ANONYMOUS]]
        anonymous_settings: RegistryEndpointAnonymousSettings
        method: Literal[RegistryEndpointAuthenticationMethod.ANONYMOUS]


    class azure.mgmt.iotoperations.types.RegistryEndpointAnonymousSettings(TypedDict, total=False):


    class azure.mgmt.iotoperations.types.RegistryEndpointArtifactPullSecretAuthentication(TypedDict, total=False):
        key "artifactPullSecretSettings": Required[RegistryEndpointArtifactPullSecretSettings]
        key "method": Required[Literal[RegistryEndpointAuthenticationMethod.ARTIFACT_PULL_SECRET]]
        artifact_pull_secret_settings: RegistryEndpointArtifactPullSecretSettings
        method: Literal[RegistryEndpointAuthenticationMethod.ARTIFACT_PULL_SECRET]


    class azure.mgmt.iotoperations.types.RegistryEndpointArtifactPullSecretSettings(TypedDict, total=False):
        key "secretRef": Required[str]
        secret_ref: str


    class azure.mgmt.iotoperations.types.RegistryEndpointAuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "Anonymous"
        ARTIFACT_PULL_SECRET = "ArtifactPullSecret"
        SYSTEM_ASSIGNED_MANAGED_IDENTITY = "SystemAssignedManagedIdentity"
        USER_ASSIGNED_MANAGED_IDENTITY = "UserAssignedManagedIdentity"


    class azure.mgmt.iotoperations.types.RegistryEndpointProperties(TypedDict, total=False):
        key "authentication": Required[RegistryEndpointAuthentication]
        key "healthState": Union[str, ResourceHealthState]
        key "host": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        authentication: RegistryEndpointAuthentication
        codeSigningCas: list[RegistryEndpointTrustedSigningKey]
        code_signing_cas: list[RegistryEndpointTrustedSigningKey]
        health_state: Union[str, ResourceHealthState]
        host: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.iotoperations.types.RegistryEndpointResource(ProxyResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "name": str
        key "properties": ForwardRef('RegistryEndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extended_location: ExtendedLocation
        id: str
        name: str
        properties: RegistryEndpointProperties
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.RegistryEndpointSystemAssignedIdentityAuthentication(TypedDict, total=False):
        key "method": Required[Literal[RegistryEndpointAuthenticationMethod.SYSTEM_ASSIGNED_MANAGED_IDENTITY]]
        key "systemAssignedManagedIdentitySettings": Required[RegistryEndpointSystemAssignedManagedIdentitySettings]
        method: Literal[RegistryEndpointAuthenticationMethod.SYSTEM_ASSIGNED_MANAGED_IDENTITY]
        system_assigned_managed_identity_settings: RegistryEndpointSystemAssignedManagedIdentitySettings


    class azure.mgmt.iotoperations.types.RegistryEndpointSystemAssignedManagedIdentitySettings(TypedDict, total=False):
        key "audience": str
        audience: str


    class azure.mgmt.iotoperations.types.RegistryEndpointTrustedSigningKeyConfigMap(TypedDict, total=False):
        key "configMapRef": Required[str]
        key "type": Required[Literal[RegistryEndpointTrustedSigningKeyType.CONFIG_MAP]]
        config_map_ref: str
        type: Literal[RegistryEndpointTrustedSigningKeyType.CONFIG_MAP]


    class azure.mgmt.iotoperations.types.RegistryEndpointTrustedSigningKeySecret(TypedDict, total=False):
        key "secretRef": Required[str]
        key "type": Required[Literal[RegistryEndpointTrustedSigningKeyType.SECRET]]
        secret_ref: str
        type: Literal[RegistryEndpointTrustedSigningKeyType.SECRET]


    class azure.mgmt.iotoperations.types.RegistryEndpointTrustedSigningKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIG_MAP = "ConfigMap"
        SECRET = "Secret"


    class azure.mgmt.iotoperations.types.RegistryEndpointUserAssignedIdentityAuthentication(TypedDict, total=False):
        key "method": Required[Literal[RegistryEndpointAuthenticationMethod.USER_ASSIGNED_MANAGED_IDENTITY]]
        key "userAssignedManagedIdentitySettings": Required[RegistryEndpointUserAssignedManagedIdentitySettings]
        method: Literal[RegistryEndpointAuthenticationMethod.USER_ASSIGNED_MANAGED_IDENTITY]
        user_assigned_managed_identity_settings: RegistryEndpointUserAssignedManagedIdentitySettings


    class azure.mgmt.iotoperations.types.RegistryEndpointUserAssignedManagedIdentitySettings(TypedDict, total=False):
        key "clientId": Required[str]
        key "scope": str
        key "tenantId": Required[str]
        client_id: str
        scope: str
        tenant_id: str


    class azure.mgmt.iotoperations.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iotoperations.types.ResourceHealthStatus(TypedDict, total=False):
        key "lastTransitionTime": str
        key "lastUpdateTime": str
        key "message": str
        key "reasonCode": str
        key "status": Union[str, ResourceHealthState]
        last_transition_time: str
        last_update_time: str
        message: str
        reason_code: str
        status: Union[str, ResourceHealthState]


    class azure.mgmt.iotoperations.types.SanForCert(TypedDict, total=False):
        key "dns": Required[list[str]]
        key "ip": Required[list[str]]
        dns: list[str]
        ip: list[str]


    class azure.mgmt.iotoperations.types.SchemaRegistryRef(TypedDict, total=False):
        key "resourceId": Required[str]
        resource_id: str


    class azure.mgmt.iotoperations.types.SecretProviderClassRef(TypedDict, total=False):
        key "resourceId": Required[str]
        resource_id: str


    class azure.mgmt.iotoperations.types.SelfCheck(TypedDict, total=False):
        key "intervalSeconds": int
        key "mode": Union[str, OperationalMode]
        key "timeoutSeconds": int
        interval_seconds: int
        mode: Union[str, OperationalMode]
        timeout_seconds: int


    class azure.mgmt.iotoperations.types.SelfTracing(TypedDict, total=False):
        key "intervalSeconds": int
        key "mode": Union[str, OperationalMode]
        interval_seconds: int
        mode: Union[str, OperationalMode]


    class azure.mgmt.iotoperations.types.StateStoreResourceRule(TypedDict, total=False):
        key "keyType": Required[Union[str, StateStoreResourceKeyTypes]]
        key "keys": Required[list[str]]
        key "method": Required[Union[str, StateStoreResourceDefinitionMethods]]
        key_type: Union[str, StateStoreResourceKeyTypes]
        keys_property: list[str]
        method: Union[str, StateStoreResourceDefinitionMethods]


    class azure.mgmt.iotoperations.types.SubscriberQueueLimit(TypedDict, total=False):
        key "length": int
        key "strategy": Union[str, SubscriberMessageDropStrategy]
        length: int
        strategy: Union[str, SubscriberMessageDropStrategy]


    class azure.mgmt.iotoperations.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.iotoperations.types.TlsCertMethod(TypedDict, total=False):
        key "certManagerCertificateSpec": ForwardRef('CertManagerCertificateSpec', module='types')
        key "manual": ForwardRef('X509ManualCertificate', module='types')
        key "mode": Required[Union[str, TlsCertMethodMode]]
        cert_manager_certificate_spec: CertManagerCertificateSpec
        manual: X509ManualCertificate
        mode: Union[str, TlsCertMethodMode]


    class azure.mgmt.iotoperations.types.TlsProperties(TypedDict, total=False):
        key "mode": Union[str, OperationalMode]
        key "trustedCaCertificateConfigMapRef": str
        mode: Union[str, OperationalMode]
        trusted_ca_certificate_config_map_ref: str


    class azure.mgmt.iotoperations.types.Traces(TypedDict, total=False):
        key "cacheSizeMegabytes": int
        key "mode": Union[str, OperationalMode]
        key "selfTracing": ForwardRef('SelfTracing', module='types')
        key "spanChannelCapacity": int
        cache_size_megabytes: int
        mode: Union[str, OperationalMode]
        self_tracing: SelfTracing
        span_channel_capacity: int


    class azure.mgmt.iotoperations.types.TrackedResource(Resource):
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


    class azure.mgmt.iotoperations.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.iotoperations.types.VolumeClaimResourceRequirements(TypedDict, total=False):
        claims: list[VolumeClaimResourceRequirementsClaims]
        limits: dict[str, str]
        requests: dict[str, str]


    class azure.mgmt.iotoperations.types.VolumeClaimResourceRequirementsClaims(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.iotoperations.types.VolumeClaimSpec(TypedDict, total=False):
        key "dataSource": ForwardRef('LocalKubernetesReference', module='types')
        key "dataSourceRef": ForwardRef('KubernetesReference', module='types')
        key "resources": ForwardRef('VolumeClaimResourceRequirements', module='types')
        key "selector": ForwardRef('VolumeClaimSpecSelector', module='types')
        key "storageClassName": str
        key "volumeMode": str
        key "volumeName": str
        accessModes: list[str]
        access_modes: list[str]
        data_source: LocalKubernetesReference
        data_source_ref: KubernetesReference
        resources: VolumeClaimResourceRequirements
        selector: VolumeClaimSpecSelector
        storage_class_name: str
        volume_mode: str
        volume_name: str


    class azure.mgmt.iotoperations.types.VolumeClaimSpecSelector(TypedDict, total=False):
        matchExpressions: list[VolumeClaimSpecSelectorMatchExpressions]
        matchLabels: dict[str, str]
        match_expressions: list[VolumeClaimSpecSelectorMatchExpressions]
        match_labels: dict[str, str]


    class azure.mgmt.iotoperations.types.VolumeClaimSpecSelectorMatchExpressions(TypedDict, total=False):
        key "key": Required[str]
        key "operator": Required[Union[str, OperatorValues]]
        key: str
        operator: Union[str, OperatorValues]
        values: list[str]
        values_property: list[str]


    class azure.mgmt.iotoperations.types.X509ManualCertificate(TypedDict, total=False):
        key "secretRef": Required[str]
        secret_ref: str


```