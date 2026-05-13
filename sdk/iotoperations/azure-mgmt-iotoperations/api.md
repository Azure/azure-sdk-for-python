```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AkriConnectorResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> AkriConnectorTemplateResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name']}, api_versions_list=['2026-03-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name', 'accept']}, api_versions_list=['2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> AkriServiceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2026-03-01'])
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> DataflowGraphResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        async def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> RegistryEndpointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
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
        registry_settings: Optional[AkriConnectorsRegistrySettings]
        replicas: Optional[int]
        tag_digest_settings: Optional[AkriConnectorsTagDigestSettings]

        @overload
        def __init__(
                self, 
                *, 
                image_name: str, 
                image_pull_policy: Optional[Union[str, AkriConnectorsImagePullPolicy]] = ..., 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'connector_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AkriConnectorResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_connector_template_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_connector_template_name: str, 
                **kwargs: Any
            ) -> AkriConnectorTemplateResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name']}, api_versions_list=['2026-03-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'akri_service_name', 'accept']}, api_versions_list=['2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                akri_service_name: str, 
                **kwargs: Any
            ) -> AkriServiceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01', params_added_on={'2026-03-01': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2026-03-01'])
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'dataflow_graph_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                dataflow_profile_name: str, 
                dataflow_graph_name: str, 
                **kwargs: Any
            ) -> DataflowGraphResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'dataflow_profile_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
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
                resource: JSON, 
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
                resource: JSON, 
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
                resource: JSON, 
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
                properties: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'registry_endpoint_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def get(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                registry_endpoint_name: str, 
                **kwargs: Any
            ) -> RegistryEndpointResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'instance_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2026-03-01'])
        def list_by_instance_resource(
                self, 
                resource_group_name: str, 
                instance_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RegistryEndpointResource]: ...


```