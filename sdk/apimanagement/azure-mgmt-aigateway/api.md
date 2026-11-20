```py
namespace azure.mgmt.aigateway

    class azure.mgmt.aigateway.AIGatewayMgmtClient: implements ContextManager 
        ai_gateway_alias_resources: AiGatewayAliasResourcesOperations
        ai_gateway_api_key_resources: AiGatewayApiKeyResourcesOperations
        ai_gateway_model_provider_resources: AiGatewayModelProviderResourcesOperations
        ai_gateway_model_resources: AiGatewayModelResourcesOperations
        ai_gateway_name_availability_operations: AiGatewayNameAvailabilityOperationsOperations
        ai_gateway_private_endpoint_connections: AiGatewayPrivateEndpointConnectionsOperations
        ai_gateway_private_link_resources: AiGatewayPrivateLinkResourcesOperations
        ai_gateway_resources: AiGatewayResourcesOperations
        ai_gateway_telemetry_exporter_resources: AiGatewayTelemetryExporterResourcesOperations
        ai_gateway_tool_server_resources: AiGatewayToolServerResourcesOperations
        ai_gateway_workspace_model_operations: AiGatewayWorkspaceModelOperationsOperations
        ai_gateway_workspace_resources: AiGatewayWorkspaceResourcesOperations
        operations: Operations

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


namespace azure.mgmt.aigateway.aio

    class azure.mgmt.aigateway.aio.AIGatewayMgmtClient: implements AsyncContextManager 
        ai_gateway_alias_resources: AiGatewayAliasResourcesOperations
        ai_gateway_api_key_resources: AiGatewayApiKeyResourcesOperations
        ai_gateway_model_provider_resources: AiGatewayModelProviderResourcesOperations
        ai_gateway_model_resources: AiGatewayModelResourcesOperations
        ai_gateway_name_availability_operations: AiGatewayNameAvailabilityOperationsOperations
        ai_gateway_private_endpoint_connections: AiGatewayPrivateEndpointConnectionsOperations
        ai_gateway_private_link_resources: AiGatewayPrivateLinkResourcesOperations
        ai_gateway_resources: AiGatewayResourcesOperations
        ai_gateway_telemetry_exporter_resources: AiGatewayTelemetryExporterResourcesOperations
        ai_gateway_tool_server_resources: AiGatewayToolServerResourcesOperations
        ai_gateway_workspace_model_operations: AiGatewayWorkspaceModelOperationsOperations
        ai_gateway_workspace_resources: AiGatewayWorkspaceResourcesOperations
        operations: Operations

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


namespace azure.mgmt.aigateway.aio.operations

    class azure.mgmt.aigateway.aio.operations.AiGatewayAliasResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'alias_id']}, api_versions_list=['2026-11-01'])
        async def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                resource: AiGatewayAliasResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                resource: AiGatewayAliasResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'alias_id', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'alias_id', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayAliasResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                properties: AiGatewayAliasUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                properties: AiGatewayAliasUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayApiKeyResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name']}, api_versions_list=['2026-11-01'])
        async def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                resource: AiGatewayApiKeyResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                resource: AiGatewayApiKeyResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayApiKeyResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def list_secrets(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> AiGatewayApiKeyValues: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name']}, api_versions_list=['2026-11-01'])
        async def regenerate_primary_key(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name']}, api_versions_list=['2026-11-01'])
        async def regenerate_secondary_key(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                properties: AiGatewayApiKeyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                properties: AiGatewayApiKeyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayModelProviderResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name']}, api_versions_list=['2026-11-01'])
        async def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                resource: AiGatewayModelProviderResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                resource: AiGatewayModelProviderResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayModelProviderResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def list_secrets(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> AiGatewayModelProviderSecrets: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                properties: AiGatewayModelProviderUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                properties: AiGatewayModelProviderUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayModelResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'model_name']}, api_versions_list=['2026-11-01'])
        async def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                resource: AiGatewayModelResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                resource: AiGatewayModelResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'model_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'model_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_model_provider(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayModelResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                properties: AiGatewayModelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                properties: AiGatewayModelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayNameAvailabilityOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: AiGatewayCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayCheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: AiGatewayCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayCheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayCheckNameAvailabilityResponse: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                resource: AiGatewayPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayPrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                resource: AiGatewayPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayPrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayPrivateEndpointConnection]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-11-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AiGatewayPrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayPrivateEndpointConnection]: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> AiGatewayPrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayPrivateLinkResource]: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[AiGatewayResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AiGatewayResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AiGatewayResource]: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayTelemetryExporterResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'telemetry_exporter_name']}, api_versions_list=['2026-11-01'])
        async def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                resource: AiGatewayTelemetryExporterResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                resource: AiGatewayTelemetryExporterResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'telemetry_exporter_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'telemetry_exporter_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayTelemetryExporterResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                properties: AiGatewayTelemetryExporterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                properties: AiGatewayTelemetryExporterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayToolServerResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name']}, api_versions_list=['2026-11-01'])
        async def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                resource: AiGatewayToolServerResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                resource: AiGatewayToolServerResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        async def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        async def get_oauth2_login_links(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                body: AiGatewayToolServerLoginLinksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayToolServerOauth2LoginLinks: ...

        @overload
        async def get_oauth2_login_links(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                body: AiGatewayToolServerLoginLinksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayToolServerOauth2LoginLinks: ...

        @overload
        async def get_oauth2_login_links(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayToolServerOauth2LoginLinks: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayToolServerResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def list_secrets(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                **kwargs: Any
            ) -> AiGatewayToolServerSecrets: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                properties: AiGatewayToolServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                properties: AiGatewayToolServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayWorkspaceModelOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayModelResource]: ...


    class azure.mgmt.aigateway.aio.operations.AiGatewayWorkspaceResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name']}, api_versions_list=['2026-11-01'])
        async def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AiGatewayWorkspaceResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                properties: AiGatewayWorkspaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                properties: AiGatewayWorkspaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...


    class azure.mgmt.aigateway.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.aigateway.models

    class azure.mgmt.aigateway.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.aigateway.models.AiGatewayAgentHook(_Model):
        authentication: Optional[AiGatewayAgentHookAuthentication]
        endpoint: Optional[AiGatewayDestinationEndpoint]
        headers: Optional[list[AiGatewayNameValuePair]]
        mode: Optional[Union[str, AiGatewayFailureMode]]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayAgentHookAuthentication] = ..., 
                endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                headers: Optional[list[AiGatewayNameValuePair]] = ..., 
                mode: Optional[Union[str, AiGatewayFailureMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAgentHookAuthentication(_Model):
        headers: Optional[list[AiGatewaySecretHeader]]
        managed_identity: Optional[AiGatewayManagedIdentityAuthentication]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[list[AiGatewaySecretHeader]] = ..., 
                managed_identity: Optional[AiGatewayManagedIdentityAuthentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAgentHookAuthenticationUpdate(_Model):
        headers: Optional[list[AiGatewaySecretHeaderUpdate]]
        managed_identity: Optional[AiGatewayManagedIdentityAuthentication]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[list[AiGatewaySecretHeaderUpdate]] = ..., 
                managed_identity: Optional[AiGatewayManagedIdentityAuthentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAgentHookUpdate(_Model):
        authentication: Optional[AiGatewayAgentHookAuthenticationUpdate]
        endpoint: Optional[AiGatewayDestinationEndpointUpdate]
        headers: Optional[list[AiGatewayNameValuePairUpdate]]
        mode: Optional[Union[str, AiGatewayFailureMode]]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayAgentHookAuthenticationUpdate] = ..., 
                endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ..., 
                headers: Optional[list[AiGatewayNameValuePairUpdate]] = ..., 
                mode: Optional[Union[str, AiGatewayFailureMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAgentHooks(_Model):
        post_model_call: Optional[AiGatewayAgentHook]
        post_tool_call: Optional[AiGatewayAgentHook]
        pre_model_call: Optional[AiGatewayAgentHook]
        pre_tool_call: Optional[AiGatewayAgentHook]

        @overload
        def __init__(
                self, 
                *, 
                post_model_call: Optional[AiGatewayAgentHook] = ..., 
                post_tool_call: Optional[AiGatewayAgentHook] = ..., 
                pre_model_call: Optional[AiGatewayAgentHook] = ..., 
                pre_tool_call: Optional[AiGatewayAgentHook] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAgentHooksUpdate(_Model):
        post_model_call: Optional[AiGatewayAgentHookUpdate]
        post_tool_call: Optional[AiGatewayAgentHookUpdate]
        pre_model_call: Optional[AiGatewayAgentHookUpdate]
        pre_tool_call: Optional[AiGatewayAgentHookUpdate]

        @overload
        def __init__(
                self, 
                *, 
                post_model_call: Optional[AiGatewayAgentHookUpdate] = ..., 
                post_tool_call: Optional[AiGatewayAgentHookUpdate] = ..., 
                pre_model_call: Optional[AiGatewayAgentHookUpdate] = ..., 
                pre_tool_call: Optional[AiGatewayAgentHookUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasFailureRule(_Model):
        exclude_for: Optional[str]
        retry_attempts: Optional[int]
        when: str

        @overload
        def __init__(
                self, 
                *, 
                exclude_for: Optional[str] = ..., 
                retry_attempts: Optional[int] = ..., 
                when: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasFailureRuleUpdate(_Model):
        exclude_for: Optional[str]
        retry_attempts: Optional[int]
        when: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                exclude_for: Optional[str] = ..., 
                retry_attempts: Optional[int] = ..., 
                when: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasProperties(_Model):
        alias_name: Optional[str]
        auto_model_selection: Optional[AiGatewayModelSelection]
        backend_models: list[AiGatewayAliasTarget]
        description: Optional[str]
        failures: Optional[list[AiGatewayAliasFailureRule]]
        gateway_endpoints: Optional[list[AiGatewayEndpoint]]
        max_retry_attempts: Optional[int]
        policies: Optional[list[AiGatewayPolicy]]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]
        selection_order: Optional[list[Union[str, AiGatewayAliasSelectionStage]]]
        session_backend_preference: Optional[AiGatewaySessionBackendPreference]
        supported_endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alias_name: Optional[str] = ..., 
                auto_model_selection: Optional[AiGatewayModelSelection] = ..., 
                backend_models: list[AiGatewayAliasTarget], 
                description: Optional[str] = ..., 
                failures: Optional[list[AiGatewayAliasFailureRule]] = ..., 
                max_retry_attempts: Optional[int] = ..., 
                policies: Optional[list[AiGatewayPolicy]] = ..., 
                selection_order: Optional[list[Union[str, AiGatewayAliasSelectionStage]]] = ..., 
                session_backend_preference: Optional[AiGatewaySessionBackendPreference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AiGatewayAliasProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayAliasProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasSelectionStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_MODEL_SELECTION = "autoModelSelection"
        PRIORITY = "priority"
        SESSION_BACKEND_PREFERENCE = "sessionBackendPreference"


    class azure.mgmt.aigateway.models.AiGatewayAliasTarget(_Model):
        priority: Optional[int]
        resource_id: str
        selector_model_name: Optional[str]
        weight: Optional[int]
        when: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                priority: Optional[int] = ..., 
                resource_id: str, 
                selector_model_name: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                when: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasTargetUpdate(_Model):
        priority: Optional[int]
        resource_id: Optional[str]
        selector_model_name: Optional[str]
        weight: Optional[int]
        when: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                priority: Optional[int] = ..., 
                resource_id: Optional[str] = ..., 
                selector_model_name: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                when: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasUpdateParameters(_Model):
        properties: Optional[AiGatewayAliasUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayAliasUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAliasUpdateProperties(_Model):
        alias_name: Optional[str]
        auto_model_selection: Optional[AiGatewayModelSelectionUpdate]
        backend_models: Optional[list[AiGatewayAliasTargetUpdate]]
        description: Optional[str]
        failures: Optional[list[AiGatewayAliasFailureRuleUpdate]]
        max_retry_attempts: Optional[int]
        policies: Optional[list[AiGatewayPolicyUpdate]]
        selection_order: Optional[list[Union[str, AiGatewayAliasSelectionStage]]]
        session_backend_preference: Optional[AiGatewaySessionBackendPreferenceUpdate]

        @overload
        def __init__(
                self, 
                *, 
                alias_name: Optional[str] = ..., 
                auto_model_selection: Optional[AiGatewayModelSelectionUpdate] = ..., 
                backend_models: Optional[list[AiGatewayAliasTargetUpdate]] = ..., 
                description: Optional[str] = ..., 
                failures: Optional[list[AiGatewayAliasFailureRuleUpdate]] = ..., 
                max_retry_attempts: Optional[int] = ..., 
                policies: Optional[list[AiGatewayPolicyUpdate]] = ..., 
                selection_order: Optional[list[Union[str, AiGatewayAliasSelectionStage]]] = ..., 
                session_backend_preference: Optional[AiGatewaySessionBackendPreferenceUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayAllowedRequestOverride(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILTER_MODELS_FOR_TOOL_COMPATIBILITY = "filterModelsForToolCompatibility"
        MODEL = "model"
        OBJECTIVE = "objective"


    class azure.mgmt.aigateway.models.AiGatewayApiKeyProperties(_Model):
        created_date: Optional[datetime]
        display_name: Optional[str]
        expiration_date: Optional[datetime]
        primary_key: Optional[str]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]
        secondary_key: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                expiration_date: Optional[datetime] = ..., 
                primary_key: Optional[str] = ..., 
                secondary_key: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayApiKeyResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AiGatewayApiKeyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayApiKeyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayApiKeyUpdateParameters(_Model):
        properties: Optional[AiGatewayApiKeyUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayApiKeyUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayApiKeyUpdateProperties(_Model):
        display_name: Optional[str]
        expiration_date: Optional[datetime]
        primary_key: Optional[str]
        secondary_key: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                expiration_date: Optional[datetime] = ..., 
                primary_key: Optional[str] = ..., 
                secondary_key: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayApiKeyValues(_Model):
        primary_key: str
        secondary_key: str

        @overload
        def __init__(
                self, 
                *, 
                primary_key: str, 
                secondary_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayApplicationInsightsConfiguration(_Model):
        connection_string: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayBackend(_Model):
        subnet: Optional[AiGatewaySubnet]

        @overload
        def __init__(
                self, 
                *, 
                subnet: Optional[AiGatewaySubnet] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayBackendUpdate(_Model):
        subnet: Optional[AiGatewaySubnetUpdate]

        @overload
        def __init__(
                self, 
                *, 
                subnet: Optional[AiGatewaySubnetUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayCheckNameAvailabilityRequest(_Model):
        name: str
        type: Literal["ApiManagement/aigateways"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayCheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: bool
        reason: Optional[Union[str, AiGatewayNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: bool, 
                reason: Optional[Union[str, AiGatewayNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayContentSafetySeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        NONE = "None"


    class azure.mgmt.aigateway.models.AiGatewayCostLimitOverride(_Model):
        amount: Decimal
        api_key_resource_id: Optional[str]
        claims: Optional[list[AiGatewayNameValuePair]]

        @overload
        def __init__(
                self, 
                *, 
                amount: Decimal, 
                api_key_resource_id: Optional[str] = ..., 
                claims: Optional[list[AiGatewayNameValuePair]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayCostLimitOverrideUpdate(_Model):
        amount: Optional[Decimal]
        api_key_resource_id: Optional[str]
        claims: Optional[list[AiGatewayNameValuePairUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                amount: Optional[Decimal] = ..., 
                api_key_resource_id: Optional[str] = ..., 
                claims: Optional[list[AiGatewayNameValuePairUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayCounterDimension(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IDENTITY = "identity"
        IP_ADDRESS = "ipAddress"


    class azure.mgmt.aigateway.models.AiGatewayCustomProviderConfiguration(_Model):
        endpoint: AiGatewayDestinationEndpoint

        @overload
        def __init__(
                self, 
                *, 
                endpoint: AiGatewayDestinationEndpoint
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayCustomProviderConfigurationUpdate(_Model):
        endpoint: Optional[AiGatewayDestinationEndpointUpdate]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayDestinationEndpoint(_Model):
        url: str

        @overload
        def __init__(
                self, 
                *, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayDestinationEndpointUpdate(_Model):
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayEndpoint(_Model):
        api: Optional[str]
        base_url: Optional[str]
        url: str


    class azure.mgmt.aigateway.models.AiGatewayFailureMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL_CLOSED = "failClosed"
        FAIL_OPEN = "failOpen"


    class azure.mgmt.aigateway.models.AiGatewayFallbackTarget(_Model):
        model_id: str

        @overload
        def __init__(
                self, 
                *, 
                model_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayFallbackTargetUpdate(_Model):
        model_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                model_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayFoundryProviderConfiguration(_Model):
        endpoint: Optional[AiGatewayDestinationEndpoint]
        resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayFoundryProviderConfigurationUpdate(_Model):
        endpoint: Optional[AiGatewayDestinationEndpointUpdate]
        resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ..., 
                resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayFrontend(_Model):
        default_hostname: Optional[str]


    class azure.mgmt.aigateway.models.AiGatewayGitHubAppAuthentication(_Model):
        app_id: Optional[str]
        installation_id: Optional[str]
        private_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                installation_id: Optional[str] = ..., 
                private_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayIpFilterAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.aigateway.models.AiGatewayManagedIdentityAuthentication(_Model):
        client_id: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayMcpUrlConfiguration(_Model):
        endpoint: AiGatewayDestinationEndpoint
        transport: Optional[Union[str, AiGatewayToolServerMcpTransport]]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: AiGatewayDestinationEndpoint, 
                transport: Optional[Union[str, AiGatewayToolServerMcpTransport]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayMcpUrlConfigurationUpdate(_Model):
        endpoint: Optional[AiGatewayDestinationEndpointUpdate]
        transport: Optional[Union[str, AiGatewayToolServerMcpTransport]]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ..., 
                transport: Optional[Union[str, AiGatewayToolServerMcpTransport]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelDeployment(_Model):
        model_name: str
        model_version: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                model_name: str, 
                model_version: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelDeploymentUpdate(_Model):
        model_name: Optional[str]
        model_version: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                model_name: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelEndpoint(_Model):
        api: str
        path: str

        @overload
        def __init__(
                self, 
                *, 
                api: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelEndpointUpdate(_Model):
        api: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProperties(_Model):
        deployment: AiGatewayModelDeployment
        description: Optional[str]
        display_name: str
        endpoints: Optional[list[AiGatewayModelEndpoint]]
        policies: Optional[list[AiGatewayPolicy]]
        provider_kind: Optional[Union[str, AiGatewayModelProviderKind]]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]
        supported_endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                deployment: AiGatewayModelDeployment, 
                description: Optional[str] = ..., 
                display_name: str, 
                endpoints: Optional[list[AiGatewayModelEndpoint]] = ..., 
                policies: Optional[list[AiGatewayPolicy]] = ..., 
                supported_endpoints: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderAuthentication(_Model):
        github_app: Optional[AiGatewayGitHubAppAuthentication]
        headers: Optional[list[AiGatewaySecretHeader]]
        managed_identity: Optional[AiGatewayManagedIdentityAuthentication]

        @overload
        def __init__(
                self, 
                *, 
                github_app: Optional[AiGatewayGitHubAppAuthentication] = ..., 
                headers: Optional[list[AiGatewaySecretHeader]] = ..., 
                managed_identity: Optional[AiGatewayManagedIdentityAuthentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderAuthenticationUpdate(_Model):
        github_app: Optional[AiGatewayGitHubAppAuthentication]
        headers: Optional[list[AiGatewaySecretHeaderUpdate]]
        managed_identity: Optional[AiGatewayManagedIdentityAuthentication]

        @overload
        def __init__(
                self, 
                *, 
                github_app: Optional[AiGatewayGitHubAppAuthentication] = ..., 
                headers: Optional[list[AiGatewaySecretHeaderUpdate]] = ..., 
                managed_identity: Optional[AiGatewayManagedIdentityAuthentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        FOUNDRY = "Foundry"
        GIT_HUB = "GitHub"


    class azure.mgmt.aigateway.models.AiGatewayModelProviderProperties(_Model):
        authentication: Optional[AiGatewayModelProviderAuthentication]
        custom: Optional[AiGatewayCustomProviderConfiguration]
        description: Optional[str]
        display_name: str
        foundry: Optional[AiGatewayFoundryProviderConfiguration]
        model_provider_type: Union[str, AiGatewayModelProviderKind]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayModelProviderAuthentication] = ..., 
                custom: Optional[AiGatewayCustomProviderConfiguration] = ..., 
                description: Optional[str] = ..., 
                display_name: str, 
                foundry: Optional[AiGatewayFoundryProviderConfiguration] = ..., 
                model_provider_type: Union[str, AiGatewayModelProviderKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AiGatewayModelProviderProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayModelProviderProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderSecretAuthentication(_Model):
        github_app: Optional[AiGatewayModelProviderSecretGitHubAppAuthentication]
        headers: Optional[list[AiGatewaySecretHeaderValue]]
        managed_identity: Optional[AiGatewayManagedIdentityAuthentication]

        @overload
        def __init__(
                self, 
                *, 
                github_app: Optional[AiGatewayModelProviderSecretGitHubAppAuthentication] = ..., 
                headers: Optional[list[AiGatewaySecretHeaderValue]] = ..., 
                managed_identity: Optional[AiGatewayManagedIdentityAuthentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderSecretGitHubAppAuthentication(_Model):
        app_id: Optional[str]
        installation_id: Optional[str]
        private_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                installation_id: Optional[str] = ..., 
                private_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderSecrets(_Model):
        authentication: Optional[AiGatewayModelProviderSecretAuthentication]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayModelProviderSecretAuthentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderUpdateParameters(_Model):
        properties: Optional[AiGatewayModelProviderUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayModelProviderUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelProviderUpdateProperties(_Model):
        authentication: Optional[AiGatewayModelProviderAuthenticationUpdate]
        custom: Optional[AiGatewayCustomProviderConfigurationUpdate]
        description: Optional[str]
        display_name: Optional[str]
        foundry: Optional[AiGatewayFoundryProviderConfigurationUpdate]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayModelProviderAuthenticationUpdate] = ..., 
                custom: Optional[AiGatewayCustomProviderConfigurationUpdate] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                foundry: Optional[AiGatewayFoundryProviderConfigurationUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AiGatewayModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelSelection(_Model):
        allowed_request_overrides: Optional[list[Union[str, AiGatewayAllowedRequestOverride]]]
        objective: Union[str, AiGatewayModelSelectionObjective]

        @overload
        def __init__(
                self, 
                *, 
                allowed_request_overrides: Optional[list[Union[str, AiGatewayAllowedRequestOverride]]] = ..., 
                objective: Union[str, AiGatewayModelSelectionObjective]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelSelectionObjective(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BALANCED = "Balanced"
        COST = "Cost"
        QUALITY = "Quality"


    class azure.mgmt.aigateway.models.AiGatewayModelSelectionUpdate(_Model):
        allowed_request_overrides: Optional[list[Union[str, AiGatewayAllowedRequestOverride]]]
        objective: Optional[Union[str, AiGatewayModelSelectionObjective]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_request_overrides: Optional[list[Union[str, AiGatewayAllowedRequestOverride]]] = ..., 
                objective: Optional[Union[str, AiGatewayModelSelectionObjective]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelUpdateParameters(_Model):
        properties: Optional[AiGatewayModelUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayModelUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayModelUpdateProperties(_Model):
        deployment: Optional[AiGatewayModelDeploymentUpdate]
        description: Optional[str]
        display_name: Optional[str]
        endpoints: Optional[list[AiGatewayModelEndpointUpdate]]
        policies: Optional[list[AiGatewayPolicyUpdate]]
        supported_endpoints: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                deployment: Optional[AiGatewayModelDeploymentUpdate] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                endpoints: Optional[list[AiGatewayModelEndpointUpdate]] = ..., 
                policies: Optional[list[AiGatewayPolicyUpdate]] = ..., 
                supported_endpoints: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.aigateway.models.AiGatewayNameValuePair(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayNameValuePairUpdate(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayOpenApiConfiguration(_Model):
        spec_source: AiGatewayOpenApiSpecSource

        @overload
        def __init__(
                self, 
                *, 
                spec_source: AiGatewayOpenApiSpecSource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayOpenApiConfigurationUpdate(_Model):
        spec_source: Optional[AiGatewayOpenApiSpecSourceUpdate]

        @overload
        def __init__(
                self, 
                *, 
                spec_source: Optional[AiGatewayOpenApiSpecSourceUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayOpenApiSpecSource(_Model):
        content_base64: Optional[bytes]
        type: Union[str, AiGatewayToolServerOpenApiSourceType]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_base64: Optional[bytes] = ..., 
                type: Union[str, AiGatewayToolServerOpenApiSourceType], 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayOpenApiSpecSourceUpdate(_Model):
        content_base64: Optional[bytes]
        type: Optional[Union[str, AiGatewayToolServerOpenApiSourceType]]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_base64: Optional[bytes] = ..., 
                type: Optional[Union[str, AiGatewayToolServerOpenApiSourceType]] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayOpenTelemetryConfiguration(_Model):
        logs_endpoint: Optional[AiGatewayDestinationEndpoint]
        metrics_endpoint: Optional[AiGatewayDestinationEndpoint]
        traces_endpoint: Optional[AiGatewayDestinationEndpoint]

        @overload
        def __init__(
                self, 
                *, 
                logs_endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                metrics_endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                traces_endpoint: Optional[AiGatewayDestinationEndpoint] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayOpenTelemetryConfigurationUpdate(_Model):
        logs_endpoint: Optional[AiGatewayDestinationEndpointUpdate]
        metrics_endpoint: Optional[AiGatewayDestinationEndpointUpdate]
        traces_endpoint: Optional[AiGatewayDestinationEndpointUpdate]

        @overload
        def __init__(
                self, 
                *, 
                logs_endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ..., 
                metrics_endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ..., 
                traces_endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayPolicy(_Model):
        action: Optional[Union[str, AiGatewayIpFilterAction]]
        allow_credentials: Optional[bool]
        allowed_headers: Optional[list[str]]
        allowed_methods: Optional[list[str]]
        allowed_origins: Optional[list[str]]
        amount: Optional[Decimal]
        authentication: Optional[AiGatewayAgentHookAuthentication]
        cidr_ranges: Optional[list[str]]
        count: Optional[int]
        counter_key: Optional[list[Union[str, AiGatewayCounterDimension]]]
        endpoint: Optional[AiGatewayDestinationEndpoint]
        expose_headers: Optional[list[str]]
        fallback_targets: Optional[list[AiGatewayFallbackTarget]]
        hate_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]
        headers: Optional[list[AiGatewayNameValuePair]]
        hooks: Optional[AiGatewayAgentHooks]
        id: Optional[str]
        mode: Optional[Union[str, AiGatewayFailureMode]]
        overrides: Optional[list[AiGatewayCostLimitOverride]]
        period: Optional[Union[str, AiGatewayPolicyPeriod]]
        post_invocation: Optional[bool]
        pre_invocation: Optional[bool]
        preflight_result_max_age: Optional[int]
        scope: Optional[Union[str, AiGatewayPolicyScope]]
        self_harm_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]
        sexual_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]
        terminate_unmatched_request: Optional[bool]
        threshold: Optional[int]
        trip_duration_seconds: Optional[int]
        type: Union[str, AiGatewayPolicyType]
        violence_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, AiGatewayIpFilterAction]] = ..., 
                allow_credentials: Optional[bool] = ..., 
                allowed_headers: Optional[list[str]] = ..., 
                allowed_methods: Optional[list[str]] = ..., 
                allowed_origins: Optional[list[str]] = ..., 
                amount: Optional[Decimal] = ..., 
                authentication: Optional[AiGatewayAgentHookAuthentication] = ..., 
                cidr_ranges: Optional[list[str]] = ..., 
                count: Optional[int] = ..., 
                counter_key: Optional[list[Union[str, AiGatewayCounterDimension]]] = ..., 
                endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                expose_headers: Optional[list[str]] = ..., 
                fallback_targets: Optional[list[AiGatewayFallbackTarget]] = ..., 
                hate_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ..., 
                headers: Optional[list[AiGatewayNameValuePair]] = ..., 
                hooks: Optional[AiGatewayAgentHooks] = ..., 
                id: Optional[str] = ..., 
                mode: Optional[Union[str, AiGatewayFailureMode]] = ..., 
                overrides: Optional[list[AiGatewayCostLimitOverride]] = ..., 
                period: Optional[Union[str, AiGatewayPolicyPeriod]] = ..., 
                post_invocation: Optional[bool] = ..., 
                pre_invocation: Optional[bool] = ..., 
                preflight_result_max_age: Optional[int] = ..., 
                scope: Optional[Union[str, AiGatewayPolicyScope]] = ..., 
                self_harm_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ..., 
                sexual_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ..., 
                terminate_unmatched_request: Optional[bool] = ..., 
                threshold: Optional[int] = ..., 
                trip_duration_seconds: Optional[int] = ..., 
                type: Union[str, AiGatewayPolicyType], 
                violence_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayPolicyPeriod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "day"
        HOUR = "hour"
        MINUTE = "minute"
        MONTH = "month"
        WEEK = "week"
        YEAR = "year"


    class azure.mgmt.aigateway.models.AiGatewayPolicyScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE = "resource"
        WORKSPACE = "workspace"


    class azure.mgmt.aigateway.models.AiGatewayPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_HOOKS = "agentHooks"
        CONTENT_SAFETY = "contentSafety"
        CORS = "cors"
        COST_LIMIT = "costLimit"
        FALLBACK = "fallback"
        IP_FILTER = "ipFilter"
        REQUEST_RATE_LIMIT = "requestRateLimit"
        TOKEN_LIMIT = "tokenLimit"
        TOOL_THREAT_PROTECTION = "toolThreatProtection"


    class azure.mgmt.aigateway.models.AiGatewayPolicyUpdate(_Model):
        action: Optional[Union[str, AiGatewayIpFilterAction]]
        allow_credentials: Optional[bool]
        allowed_headers: Optional[list[str]]
        allowed_methods: Optional[list[str]]
        allowed_origins: Optional[list[str]]
        amount: Optional[Decimal]
        authentication: Optional[AiGatewayAgentHookAuthenticationUpdate]
        cidr_ranges: Optional[list[str]]
        count: Optional[int]
        counter_key: Optional[list[Union[str, AiGatewayCounterDimension]]]
        endpoint: Optional[AiGatewayDestinationEndpointUpdate]
        expose_headers: Optional[list[str]]
        fallback_targets: Optional[list[AiGatewayFallbackTargetUpdate]]
        hate_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]
        headers: Optional[list[AiGatewayNameValuePairUpdate]]
        hooks: Optional[AiGatewayAgentHooksUpdate]
        id: Optional[str]
        mode: Optional[Union[str, AiGatewayFailureMode]]
        overrides: Optional[list[AiGatewayCostLimitOverrideUpdate]]
        period: Optional[Union[str, AiGatewayPolicyPeriod]]
        post_invocation: Optional[bool]
        pre_invocation: Optional[bool]
        preflight_result_max_age: Optional[int]
        scope: Optional[Union[str, AiGatewayPolicyScope]]
        self_harm_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]
        sexual_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]
        terminate_unmatched_request: Optional[bool]
        threshold: Optional[int]
        trip_duration_seconds: Optional[int]
        type: Optional[Union[str, AiGatewayPolicyType]]
        violence_severity: Optional[Union[str, AiGatewayContentSafetySeverity]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, AiGatewayIpFilterAction]] = ..., 
                allow_credentials: Optional[bool] = ..., 
                allowed_headers: Optional[list[str]] = ..., 
                allowed_methods: Optional[list[str]] = ..., 
                allowed_origins: Optional[list[str]] = ..., 
                amount: Optional[Decimal] = ..., 
                authentication: Optional[AiGatewayAgentHookAuthenticationUpdate] = ..., 
                cidr_ranges: Optional[list[str]] = ..., 
                count: Optional[int] = ..., 
                counter_key: Optional[list[Union[str, AiGatewayCounterDimension]]] = ..., 
                endpoint: Optional[AiGatewayDestinationEndpointUpdate] = ..., 
                expose_headers: Optional[list[str]] = ..., 
                fallback_targets: Optional[list[AiGatewayFallbackTargetUpdate]] = ..., 
                hate_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ..., 
                headers: Optional[list[AiGatewayNameValuePairUpdate]] = ..., 
                hooks: Optional[AiGatewayAgentHooksUpdate] = ..., 
                id: Optional[str] = ..., 
                mode: Optional[Union[str, AiGatewayFailureMode]] = ..., 
                overrides: Optional[list[AiGatewayCostLimitOverrideUpdate]] = ..., 
                period: Optional[Union[str, AiGatewayPolicyPeriod]] = ..., 
                post_invocation: Optional[bool] = ..., 
                pre_invocation: Optional[bool] = ..., 
                preflight_result_max_age: Optional[int] = ..., 
                scope: Optional[Union[str, AiGatewayPolicyScope]] = ..., 
                self_harm_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ..., 
                sexual_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ..., 
                terminate_unmatched_request: Optional[bool] = ..., 
                threshold: Optional[int] = ..., 
                trip_duration_seconds: Optional[int] = ..., 
                type: Optional[Union[str, AiGatewayPolicyType]] = ..., 
                violence_severity: Optional[Union[str, AiGatewayContentSafetySeverity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayPrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayPrivateLinkResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayProperties(_Model):
        backend: Optional[AiGatewayBackend]
        frontend: Optional[AiGatewayFrontend]
        private_endpoint_connections: Optional[list[AiGatewayPrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]
        public_network_access: Optional[Union[str, AiGatewayPublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                backend: Optional[AiGatewayBackend] = ..., 
                public_network_access: Optional[Union[str, AiGatewayPublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.aigateway.models.AiGatewayPublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.aigateway.models.AiGatewayResource(TrackedResource):
        e_tag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: AiGatewayProperties
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: AiGatewayProperties, 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySecretHeader(_Model):
        name: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySecretHeaderUpdate(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySecretHeaderValue(_Model):
        name: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySessionBackendPreference(_Model):
        key: str

        @overload
        def __init__(
                self, 
                *, 
                key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySessionBackendPreferenceUpdate(_Model):
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySkuUpdate(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: Optional[str]
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySubnet(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewaySubnetUpdate(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryAttributeMapping(_Model):
        signals: Optional[list[Union[str, AiGatewayTelemetrySignal]]]
        source: AiGatewayTelemetryAttributeSource

        @overload
        def __init__(
                self, 
                *, 
                signals: Optional[list[Union[str, AiGatewayTelemetrySignal]]] = ..., 
                source: AiGatewayTelemetryAttributeSource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryAttributeMappingUpdate(_Model):
        signals: Optional[list[Union[str, AiGatewayTelemetrySignal]]]
        source: Optional[AiGatewayTelemetryAttributeSourceUpdate]

        @overload
        def __init__(
                self, 
                *, 
                signals: Optional[list[Union[str, AiGatewayTelemetrySignal]]] = ..., 
                source: Optional[AiGatewayTelemetryAttributeSourceUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryAttributeSource(_Model):
        kind: Literal["claims"]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryAttributeSourceUpdate(_Model):
        kind: Optional[Literal["claims"]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Literal[claims]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryAuthentication(_Model):
        headers: Optional[list[AiGatewaySecretHeader]]
        managed_identity: Optional[AiGatewayTelemetryManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[list[AiGatewaySecretHeader]] = ..., 
                managed_identity: Optional[AiGatewayTelemetryManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryAuthenticationUpdate(_Model):
        headers: Optional[list[AiGatewaySecretHeaderUpdate]]
        managed_identity: Optional[AiGatewayTelemetryManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[list[AiGatewaySecretHeaderUpdate]] = ..., 
                managed_identity: Optional[AiGatewayTelemetryManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryConfiguration(_Model):
        attributes: Optional[list[AiGatewayTelemetryAttributeMapping]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[list[AiGatewayTelemetryAttributeMapping]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryConfigurationUpdate(_Model):
        attributes: Optional[list[AiGatewayTelemetryAttributeMappingUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[list[AiGatewayTelemetryAttributeMappingUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryExporterKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_INSIGHTS = "ApplicationInsights"
        OPEN_TELEMETRY = "OpenTelemetry"


    class azure.mgmt.aigateway.models.AiGatewayTelemetryExporterProperties(_Model):
        application_insights: Optional[AiGatewayApplicationInsightsConfiguration]
        authentication: Optional[AiGatewayTelemetryAuthentication]
        open_telemetry: Optional[AiGatewayOpenTelemetryConfiguration]
        payload_capture: Optional[bool]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]
        telemetry: Optional[AiGatewayTelemetryConfiguration]
        telemetry_exporter_type: Union[str, AiGatewayTelemetryExporterKind]

        @overload
        def __init__(
                self, 
                *, 
                application_insights: Optional[AiGatewayApplicationInsightsConfiguration] = ..., 
                authentication: Optional[AiGatewayTelemetryAuthentication] = ..., 
                open_telemetry: Optional[AiGatewayOpenTelemetryConfiguration] = ..., 
                payload_capture: Optional[bool] = ..., 
                telemetry: Optional[AiGatewayTelemetryConfiguration] = ..., 
                telemetry_exporter_type: Union[str, AiGatewayTelemetryExporterKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryExporterResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AiGatewayTelemetryExporterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayTelemetryExporterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryExporterUpdateParameters(_Model):
        properties: Optional[AiGatewayTelemetryExporterUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayTelemetryExporterUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryExporterUpdateProperties(_Model):
        application_insights: Optional[AiGatewayApplicationInsightsConfiguration]
        authentication: Optional[AiGatewayTelemetryAuthenticationUpdate]
        open_telemetry: Optional[AiGatewayOpenTelemetryConfigurationUpdate]
        payload_capture: Optional[bool]
        telemetry: Optional[AiGatewayTelemetryConfigurationUpdate]

        @overload
        def __init__(
                self, 
                *, 
                application_insights: Optional[AiGatewayApplicationInsightsConfiguration] = ..., 
                authentication: Optional[AiGatewayTelemetryAuthenticationUpdate] = ..., 
                open_telemetry: Optional[AiGatewayOpenTelemetryConfigurationUpdate] = ..., 
                payload_capture: Optional[bool] = ..., 
                telemetry: Optional[AiGatewayTelemetryConfigurationUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetryManagedIdentity(_Model):
        client_id: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayTelemetrySignal(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGS = "logs"
        METRICS = "metrics"
        TRACES = "traces"


    class azure.mgmt.aigateway.models.AiGatewayToolServerAccessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        BLOCKED = "blocked"


    class azure.mgmt.aigateway.models.AiGatewayToolServerAuthentication(_Model):
        headers: Optional[list[AiGatewaySecretHeader]]
        managed_identity: Optional[AiGatewayToolServerManagedIdentityAuthentication]
        oauth2: Optional[AiGatewayToolServerOauth2Authentication]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[list[AiGatewaySecretHeader]] = ..., 
                managed_identity: Optional[AiGatewayToolServerManagedIdentityAuthentication] = ..., 
                oauth2: Optional[AiGatewayToolServerOauth2Authentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerAuthenticationUpdate(_Model):
        headers: Optional[list[AiGatewaySecretHeaderUpdate]]
        managed_identity: Optional[AiGatewayToolServerManagedIdentityAuthentication]
        oauth2: Optional[AiGatewayToolServerOauth2Authentication]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[list[AiGatewaySecretHeaderUpdate]] = ..., 
                managed_identity: Optional[AiGatewayToolServerManagedIdentityAuthentication] = ..., 
                oauth2: Optional[AiGatewayToolServerOauth2Authentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerEndpoint(_Model):
        authentication: Optional[AiGatewayToolServerAuthentication]
        id: Optional[str]
        kind: Union[str, AiGatewayToolServerEndpointSourceKind]
        mcp: Optional[AiGatewayMcpUrlConfiguration]
        mode: Optional[Union[str, AiGatewayFailureMode]]
        namespace: Optional[str]
        open_api: Optional[AiGatewayOpenApiConfiguration]
        tools: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayToolServerAuthentication] = ..., 
                id: Optional[str] = ..., 
                kind: Union[str, AiGatewayToolServerEndpointSourceKind], 
                mcp: Optional[AiGatewayMcpUrlConfiguration] = ..., 
                mode: Optional[Union[str, AiGatewayFailureMode]] = ..., 
                namespace: Optional[str] = ..., 
                open_api: Optional[AiGatewayOpenApiConfiguration] = ..., 
                tools: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerEndpointSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MCP = "mcp"
        OPEN_API = "openApi"


    class azure.mgmt.aigateway.models.AiGatewayToolServerEndpointUpdate(_Model):
        authentication: Optional[AiGatewayToolServerAuthenticationUpdate]
        id: Optional[str]
        kind: Optional[Union[str, AiGatewayToolServerEndpointSourceKind]]
        mcp: Optional[AiGatewayMcpUrlConfigurationUpdate]
        mode: Optional[Union[str, AiGatewayFailureMode]]
        namespace: Optional[str]
        open_api: Optional[AiGatewayOpenApiConfigurationUpdate]
        tools: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayToolServerAuthenticationUpdate] = ..., 
                id: Optional[str] = ..., 
                kind: Optional[Union[str, AiGatewayToolServerEndpointSourceKind]] = ..., 
                mcp: Optional[AiGatewayMcpUrlConfigurationUpdate] = ..., 
                mode: Optional[Union[str, AiGatewayFailureMode]] = ..., 
                namespace: Optional[str] = ..., 
                open_api: Optional[AiGatewayOpenApiConfigurationUpdate] = ..., 
                tools: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerFederation(_Model):
        app_credential: Optional[AiGatewayToolServerFederationAppCredential]
        application_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_credential: Optional[AiGatewayToolServerFederationAppCredential] = ..., 
                application_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerFederationAppCredential(_Model):
        client_id: Optional[str]
        type: Union[str, AiGatewayToolServerFederationAppCredentialType]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                type: Union[str, AiGatewayToolServerFederationAppCredentialType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerFederationAppCredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USER_ASSIGNED_MANAGED_IDENTITY = "userAssignedManagedIdentity"


    class azure.mgmt.aigateway.models.AiGatewayToolServerLoginLinksRequest(_Model):
        endpoint_id: str

        @overload
        def __init__(
                self, 
                *, 
                endpoint_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerManagedIdentityAuthentication(_Model):
        client_id: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerMcpTransport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STREAMABLE_HTTP = "streamableHttp"


    class azure.mgmt.aigateway.models.AiGatewayToolServerOauth2Authentication(_Model):
        authorization_endpoint: Optional[AiGatewayDestinationEndpoint]
        authorization_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]]
        client_id: Optional[str]
        client_secret: Optional[str]
        grant_type: Optional[Union[str, AiGatewayToolServerOauth2GrantType]]
        issuer: Optional[str]
        login_link: Optional[str]
        scopes: Optional[list[str]]
        status: Optional[str]
        status_updated_utc: Optional[datetime]
        token_endpoint: Optional[AiGatewayDestinationEndpoint]
        token_exchange: Optional[AiGatewayToolServerTokenExchange]
        token_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]]

        @overload
        def __init__(
                self, 
                *, 
                authorization_endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                authorization_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                grant_type: Optional[Union[str, AiGatewayToolServerOauth2GrantType]] = ..., 
                issuer: Optional[str] = ..., 
                scopes: Optional[list[str]] = ..., 
                token_endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                token_exchange: Optional[AiGatewayToolServerTokenExchange] = ..., 
                token_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerOauth2GrantType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTHORIZATION_CODE = "authorizationCode"
        CLIENT_CREDENTIALS = "clientCredentials"


    class azure.mgmt.aigateway.models.AiGatewayToolServerOauth2LoginLinks(_Model):
        expires_utc: datetime
        login_link: Optional[str]
        redirect_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expires_utc: datetime, 
                login_link: Optional[str] = ..., 
                redirect_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerOauth2Parameter(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerOpenApiSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        URL = "url"


    class azure.mgmt.aigateway.models.AiGatewayToolServerProperties(_Model):
        access_state: Optional[Union[str, AiGatewayToolServerAccessState]]
        allow_list: Optional[list[str]]
        block_list: Optional[list[str]]
        description: Optional[str]
        display_name: Optional[str]
        endpoints: Optional[list[AiGatewayToolServerEndpoint]]
        gateway_endpoints: Optional[list[AiGatewayEndpoint]]
        path: Optional[str]
        policies: Optional[list[AiGatewayPolicy]]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]
        subscription_required: Optional[bool]
        tool_server_type: Union[str, AiGatewayToolServerType]
        versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                access_state: Optional[Union[str, AiGatewayToolServerAccessState]] = ..., 
                allow_list: Optional[list[str]] = ..., 
                block_list: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                endpoints: Optional[list[AiGatewayToolServerEndpoint]] = ..., 
                path: Optional[str] = ..., 
                policies: Optional[list[AiGatewayPolicy]] = ..., 
                subscription_required: Optional[bool] = ..., 
                tool_server_type: Union[str, AiGatewayToolServerType], 
                versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AiGatewayToolServerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayToolServerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerSecret(_Model):
        authentication: Optional[AiGatewayToolServerSecretAuthentication]
        id: str
        open_api: Optional[AiGatewayToolServerSecretOpenApiConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[AiGatewayToolServerSecretAuthentication] = ..., 
                id: str, 
                open_api: Optional[AiGatewayToolServerSecretOpenApiConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerSecretAuthentication(_Model):
        headers: Optional[list[AiGatewaySecretHeaderValue]]
        managed_identity: Optional[AiGatewayToolServerManagedIdentityAuthentication]
        oauth2: Optional[AiGatewayToolServerSecretOauth2Authentication]

        @overload
        def __init__(
                self, 
                *, 
                headers: Optional[list[AiGatewaySecretHeaderValue]] = ..., 
                managed_identity: Optional[AiGatewayToolServerManagedIdentityAuthentication] = ..., 
                oauth2: Optional[AiGatewayToolServerSecretOauth2Authentication] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerSecretOauth2Authentication(_Model):
        authorization_endpoint: Optional[AiGatewayDestinationEndpoint]
        authorization_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]]
        client_id: Optional[str]
        client_secret: Optional[str]
        grant_type: Optional[Union[str, AiGatewayToolServerOauth2GrantType]]
        issuer: Optional[str]
        login_link: Optional[str]
        scopes: Optional[list[str]]
        status: Optional[str]
        status_updated_utc: Optional[datetime]
        token_endpoint: Optional[AiGatewayDestinationEndpoint]
        token_exchange: Optional[AiGatewayToolServerTokenExchange]
        token_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]]

        @overload
        def __init__(
                self, 
                *, 
                authorization_endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                authorization_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                grant_type: Optional[Union[str, AiGatewayToolServerOauth2GrantType]] = ..., 
                issuer: Optional[str] = ..., 
                scopes: Optional[list[str]] = ..., 
                token_endpoint: Optional[AiGatewayDestinationEndpoint] = ..., 
                token_exchange: Optional[AiGatewayToolServerTokenExchange] = ..., 
                token_parameters: Optional[list[AiGatewayToolServerOauth2Parameter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerSecretOpenApiConfiguration(_Model):
        spec_source: AiGatewayToolServerSecretOpenApiSpecSource

        @overload
        def __init__(
                self, 
                *, 
                spec_source: AiGatewayToolServerSecretOpenApiSpecSource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerSecretOpenApiSpecSource(_Model):
        content_base64: Optional[bytes]
        type: Union[str, AiGatewayToolServerOpenApiSourceType]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_base64: Optional[bytes] = ..., 
                type: Union[str, AiGatewayToolServerOpenApiSourceType], 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerSecrets(_Model):
        endpoints: list[AiGatewayToolServerSecret]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: list[AiGatewayToolServerSecret]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerTokenExchange(_Model):
        federated_client_application: Optional[AiGatewayToolServerFederation]
        profile: Union[str, AiGatewayToolServerTokenExchangeProfile]
        scopes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                federated_client_application: Optional[AiGatewayToolServerFederation] = ..., 
                profile: Union[str, AiGatewayToolServerTokenExchangeProfile], 
                scopes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerTokenExchangeProfile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTRA_ON_BEHALF_OF = "entraOnBehalfOf"


    class azure.mgmt.aigateway.models.AiGatewayToolServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTOR = "connector"
        MCP = "mcp"
        OPEN_API = "openApi"


    class azure.mgmt.aigateway.models.AiGatewayToolServerUpdateParameters(_Model):
        properties: Optional[AiGatewayToolServerUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayToolServerUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayToolServerUpdateProperties(_Model):
        access_state: Optional[Union[str, AiGatewayToolServerAccessState]]
        allow_list: Optional[list[str]]
        block_list: Optional[list[str]]
        description: Optional[str]
        display_name: Optional[str]
        endpoints: Optional[list[AiGatewayToolServerEndpointUpdate]]
        path: Optional[str]
        policies: Optional[list[AiGatewayPolicyUpdate]]
        subscription_required: Optional[bool]
        tool_server_type: Optional[Union[str, AiGatewayToolServerType]]
        versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                access_state: Optional[Union[str, AiGatewayToolServerAccessState]] = ..., 
                allow_list: Optional[list[str]] = ..., 
                block_list: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                endpoints: Optional[list[AiGatewayToolServerEndpointUpdate]] = ..., 
                path: Optional[str] = ..., 
                policies: Optional[list[AiGatewayPolicyUpdate]] = ..., 
                subscription_required: Optional[bool] = ..., 
                tool_server_type: Optional[Union[str, AiGatewayToolServerType]] = ..., 
                versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[AiGatewayUpdateProperties]
        sku: Optional[AiGatewaySkuUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[AiGatewayUpdateProperties] = ..., 
                sku: Optional[AiGatewaySkuUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayUpdateProperties(_Model):
        backend: Optional[AiGatewayBackendUpdate]
        public_network_access: Optional[Union[str, AiGatewayPublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                backend: Optional[AiGatewayBackendUpdate] = ..., 
                public_network_access: Optional[Union[str, AiGatewayPublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayWorkspaceProperties(_Model):
        description: str
        display_name: str
        policies: Optional[list[AiGatewayPolicy]]
        provisioning_state: Optional[Union[str, AiGatewayProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                policies: Optional[list[AiGatewayPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayWorkspaceResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AiGatewayWorkspaceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayWorkspaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayWorkspaceUpdateParameters(_Model):
        properties: Optional[AiGatewayWorkspaceUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AiGatewayWorkspaceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.AiGatewayWorkspaceUpdateProperties(_Model):
        policies: Optional[list[AiGatewayPolicyUpdate]]

        @overload
        def __init__(
                self, 
                *, 
                policies: Optional[list[AiGatewayPolicyUpdate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.aigateway.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.aigateway.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.aigateway.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.aigateway.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.aigateway.models.Operation(_Model):
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


    class azure.mgmt.aigateway.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.aigateway.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.aigateway.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.aigateway.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.aigateway.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.aigateway.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.aigateway.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.aigateway.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.aigateway.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.aigateway.models.SystemData(_Model):
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


    class azure.mgmt.aigateway.models.TrackedResource(Resource):
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


    class azure.mgmt.aigateway.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.aigateway.operations

    class azure.mgmt.aigateway.operations.AiGatewayAliasResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'alias_id']}, api_versions_list=['2026-11-01'])
        def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                resource: AiGatewayAliasResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                resource: AiGatewayAliasResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'alias_id', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'alias_id', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayAliasResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                properties: AiGatewayAliasUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                properties: AiGatewayAliasUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                alias_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayAliasResource: ...


    class azure.mgmt.aigateway.operations.AiGatewayApiKeyResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name']}, api_versions_list=['2026-11-01'])
        def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                resource: AiGatewayApiKeyResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                resource: AiGatewayApiKeyResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayApiKeyResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_secrets(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> AiGatewayApiKeyValues: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name']}, api_versions_list=['2026-11-01'])
        def regenerate_primary_key(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'api_key_name']}, api_versions_list=['2026-11-01'])
        def regenerate_secondary_key(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                properties: AiGatewayApiKeyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                properties: AiGatewayApiKeyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                api_key_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayApiKeyResource: ...


    class azure.mgmt.aigateway.operations.AiGatewayModelProviderResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name']}, api_versions_list=['2026-11-01'])
        def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                resource: AiGatewayModelProviderResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                resource: AiGatewayModelProviderResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayModelProviderResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_secrets(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> AiGatewayModelProviderSecrets: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                properties: AiGatewayModelProviderUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                properties: AiGatewayModelProviderUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelProviderResource: ...


    class azure.mgmt.aigateway.operations.AiGatewayModelResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'model_name']}, api_versions_list=['2026-11-01'])
        def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                resource: AiGatewayModelResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                resource: AiGatewayModelResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'model_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'model_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'model_provider_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_model_provider(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayModelResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                properties: AiGatewayModelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                properties: AiGatewayModelUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                model_provider_name: str, 
                model_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayModelResource: ...


    class azure.mgmt.aigateway.operations.AiGatewayNameAvailabilityOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: AiGatewayCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayCheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: AiGatewayCheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayCheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayCheckNameAvailabilityResponse: ...


    class azure.mgmt.aigateway.operations.AiGatewayPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                resource: AiGatewayPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayPrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                resource: AiGatewayPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayPrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayPrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-11-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AiGatewayPrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayPrivateEndpointConnection]: ...


    class azure.mgmt.aigateway.operations.AiGatewayPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> AiGatewayPrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayPrivateLinkResource]: ...


    class azure.mgmt.aigateway.operations.AiGatewayResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: AiGatewayResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: AiGatewayUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[AiGatewayResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> AiGatewayResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AiGatewayResource]: ...


    class azure.mgmt.aigateway.operations.AiGatewayTelemetryExporterResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'telemetry_exporter_name']}, api_versions_list=['2026-11-01'])
        def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                resource: AiGatewayTelemetryExporterResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                resource: AiGatewayTelemetryExporterResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'telemetry_exporter_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'telemetry_exporter_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayTelemetryExporterResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                properties: AiGatewayTelemetryExporterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                properties: AiGatewayTelemetryExporterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                telemetry_exporter_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayTelemetryExporterResource: ...


    class azure.mgmt.aigateway.operations.AiGatewayToolServerResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name']}, api_versions_list=['2026-11-01'])
        def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                resource: AiGatewayToolServerResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                resource: AiGatewayToolServerResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name', 'etag', 'match_condition']}, api_versions_list=['2026-11-01'])
        def delete(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        def get_oauth2_login_links(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                body: AiGatewayToolServerLoginLinksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayToolServerOauth2LoginLinks: ...

        @overload
        def get_oauth2_login_links(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                body: AiGatewayToolServerLoginLinksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayToolServerOauth2LoginLinks: ...

        @overload
        def get_oauth2_login_links(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AiGatewayToolServerOauth2LoginLinks: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayToolServerResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'tool_server_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_secrets(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                **kwargs: Any
            ) -> AiGatewayToolServerSecrets: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                properties: AiGatewayToolServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                properties: AiGatewayToolServerUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                tool_server_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayToolServerResource: ...


    class azure.mgmt.aigateway.operations.AiGatewayWorkspaceModelOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayModelResource]: ...


    class azure.mgmt.aigateway.operations.AiGatewayWorkspaceResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name']}, api_versions_list=['2026-11-01'])
        def check_existence(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'workspace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'ai_gateway_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_ai_gateway(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AiGatewayWorkspaceResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                properties: AiGatewayWorkspaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                properties: AiGatewayWorkspaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_gateway_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AiGatewayWorkspaceResource: ...


    class azure.mgmt.aigateway.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.aigateway.types

    class azure.mgmt.aigateway.types.AiGatewayAgentHook(TypedDict, total=False):
        key "authentication": ForwardRef('AiGatewayAgentHookAuthentication', module='types')
        key "endpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        key "mode": Union[str, AiGatewayFailureMode]
        authentication: AiGatewayAgentHookAuthentication
        endpoint: AiGatewayDestinationEndpoint
        headers: list[AiGatewayNameValuePair]
        mode: Union[str, AiGatewayFailureMode]


    class azure.mgmt.aigateway.types.AiGatewayAgentHookAuthentication(TypedDict, total=False):
        key "managedIdentity": ForwardRef('AiGatewayManagedIdentityAuthentication', module='types')
        headers: list[AiGatewaySecretHeader]
        managedIdentity: AiGatewayManagedIdentityAuthentication


    class azure.mgmt.aigateway.types.AiGatewayAgentHookAuthenticationUpdate(TypedDict, total=False):
        key "managedIdentity": ForwardRef('AiGatewayManagedIdentityAuthentication', module='types')
        headers: list[AiGatewaySecretHeaderUpdate]
        managedIdentity: AiGatewayManagedIdentityAuthentication


    class azure.mgmt.aigateway.types.AiGatewayAgentHookUpdate(TypedDict, total=False):
        key "authentication": ForwardRef('AiGatewayAgentHookAuthenticationUpdate', module='types')
        key "endpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        key "mode": Union[str, AiGatewayFailureMode]
        authentication: AiGatewayAgentHookAuthenticationUpdate
        endpoint: AiGatewayDestinationEndpointUpdate
        headers: list[AiGatewayNameValuePairUpdate]
        mode: Union[str, AiGatewayFailureMode]


    class azure.mgmt.aigateway.types.AiGatewayAgentHooks(TypedDict, total=False):
        key "postModelCall": ForwardRef('AiGatewayAgentHook', module='types')
        key "postToolCall": ForwardRef('AiGatewayAgentHook', module='types')
        key "preModelCall": ForwardRef('AiGatewayAgentHook', module='types')
        key "preToolCall": ForwardRef('AiGatewayAgentHook', module='types')
        postModelCall: AiGatewayAgentHook
        postToolCall: AiGatewayAgentHook
        preModelCall: AiGatewayAgentHook
        preToolCall: AiGatewayAgentHook


    class azure.mgmt.aigateway.types.AiGatewayAgentHooksUpdate(TypedDict, total=False):
        key "postModelCall": ForwardRef('AiGatewayAgentHookUpdate', module='types')
        key "postToolCall": ForwardRef('AiGatewayAgentHookUpdate', module='types')
        key "preModelCall": ForwardRef('AiGatewayAgentHookUpdate', module='types')
        key "preToolCall": ForwardRef('AiGatewayAgentHookUpdate', module='types')
        postModelCall: AiGatewayAgentHookUpdate
        postToolCall: AiGatewayAgentHookUpdate
        preModelCall: AiGatewayAgentHookUpdate
        preToolCall: AiGatewayAgentHookUpdate


    class azure.mgmt.aigateway.types.AiGatewayAliasFailureRule(TypedDict, total=False):
        key "excludeFor": str
        key "retryAttempts": int
        key "when": Required[str]
        excludeFor: str
        retryAttempts: int
        when: str


    class azure.mgmt.aigateway.types.AiGatewayAliasFailureRuleUpdate(TypedDict, total=False):
        key "excludeFor": str
        key "retryAttempts": int
        key "when": str
        excludeFor: str
        retryAttempts: int
        when: str


    class azure.mgmt.aigateway.types.AiGatewayAliasProperties(TypedDict, total=False):
        key "aliasName": str
        key "autoModelSelection": ForwardRef('AiGatewayModelSelection', module='types')
        key "backendModels": Required[list[AiGatewayAliasTarget]]
        key "description": str
        key "maxRetryAttempts": int
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        key "sessionBackendPreference": ForwardRef('AiGatewaySessionBackendPreference', module='types')
        aliasName: str
        autoModelSelection: AiGatewayModelSelection
        backendModels: list[AiGatewayAliasTarget]
        description: str
        failures: list[AiGatewayAliasFailureRule]
        gatewayEndpoints: list[AiGatewayEndpoint]
        maxRetryAttempts: int
        policies: list[AiGatewayPolicy]
        provisioningState: Union[str, AiGatewayProvisioningState]
        selectionOrder: list[Union[str, AiGatewayAliasSelectionStage]]
        sessionBackendPreference: AiGatewaySessionBackendPreference
        supportedEndpoints: list[str]


    class azure.mgmt.aigateway.types.AiGatewayAliasResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AiGatewayAliasProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AiGatewayAliasProperties
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.AiGatewayAliasTarget(TypedDict, total=False):
        key "priority": int
        key "resourceId": Required[str]
        key "selectorModelName": str
        key "weight": int
        key "when": str
        priority: int
        resourceId: str
        selectorModelName: str
        weight: int
        when: str


    class azure.mgmt.aigateway.types.AiGatewayAliasTargetUpdate(TypedDict, total=False):
        key "priority": int
        key "resourceId": str
        key "selectorModelName": str
        key "weight": int
        key "when": str
        priority: int
        resourceId: str
        selectorModelName: str
        weight: int
        when: str


    class azure.mgmt.aigateway.types.AiGatewayAliasUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AiGatewayAliasUpdateProperties', module='types')
        properties: AiGatewayAliasUpdateProperties


    class azure.mgmt.aigateway.types.AiGatewayAliasUpdateProperties(TypedDict, total=False):
        key "aliasName": str
        key "autoModelSelection": ForwardRef('AiGatewayModelSelectionUpdate', module='types')
        key "description": str
        key "maxRetryAttempts": int
        key "sessionBackendPreference": ForwardRef('AiGatewaySessionBackendPreferenceUpdate', module='types')
        aliasName: str
        autoModelSelection: AiGatewayModelSelectionUpdate
        backendModels: list[AiGatewayAliasTargetUpdate]
        description: str
        failures: list[AiGatewayAliasFailureRuleUpdate]
        maxRetryAttempts: int
        policies: list[AiGatewayPolicyUpdate]
        selectionOrder: list[Union[str, AiGatewayAliasSelectionStage]]
        sessionBackendPreference: AiGatewaySessionBackendPreferenceUpdate


    class azure.mgmt.aigateway.types.AiGatewayApiKeyProperties(TypedDict, total=False):
        key "createdDate": str
        key "displayName": str
        key "expirationDate": str
        key "primaryKey": str
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        key "secondaryKey": str
        key "state": str
        createdDate: str
        displayName: str
        expirationDate: str
        primaryKey: str
        provisioningState: Union[str, AiGatewayProvisioningState]
        secondaryKey: str
        state: str


    class azure.mgmt.aigateway.types.AiGatewayApiKeyResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AiGatewayApiKeyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AiGatewayApiKeyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.AiGatewayApiKeyUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AiGatewayApiKeyUpdateProperties', module='types')
        properties: AiGatewayApiKeyUpdateProperties


    class azure.mgmt.aigateway.types.AiGatewayApiKeyUpdateProperties(TypedDict, total=False):
        key "displayName": str
        key "expirationDate": str
        key "primaryKey": str
        key "secondaryKey": str
        key "state": str
        displayName: str
        expirationDate: str
        primaryKey: str
        secondaryKey: str
        state: str


    class azure.mgmt.aigateway.types.AiGatewayApplicationInsightsConfiguration(TypedDict, total=False):
        key "connectionString": str
        key "resourceId": str
        connectionString: str
        resourceId: str


    class azure.mgmt.aigateway.types.AiGatewayBackend(TypedDict, total=False):
        key "subnet": ForwardRef('AiGatewaySubnet', module='types')
        subnet: AiGatewaySubnet


    class azure.mgmt.aigateway.types.AiGatewayBackendUpdate(TypedDict, total=False):
        key "subnet": ForwardRef('AiGatewaySubnetUpdate', module='types')
        subnet: AiGatewaySubnetUpdate


    class azure.mgmt.aigateway.types.AiGatewayCheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["ApiManagement/aigateways"]]
        name: str
        type: Literal[ApiManagement/aigateways]


    class azure.mgmt.aigateway.types.AiGatewayCostLimitOverride(TypedDict, total=False):
        key "amount": Required[float]
        key "apiKeyResourceId": str
        amount: float
        apiKeyResourceId: str
        claims: list[AiGatewayNameValuePair]


    class azure.mgmt.aigateway.types.AiGatewayCostLimitOverrideUpdate(TypedDict, total=False):
        key "amount": float
        key "apiKeyResourceId": str
        amount: float
        apiKeyResourceId: str
        claims: list[AiGatewayNameValuePairUpdate]


    class azure.mgmt.aigateway.types.AiGatewayCustomProviderConfiguration(TypedDict, total=False):
        key "endpoint": Required[AiGatewayDestinationEndpoint]
        endpoint: AiGatewayDestinationEndpoint


    class azure.mgmt.aigateway.types.AiGatewayCustomProviderConfigurationUpdate(TypedDict, total=False):
        key "endpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        endpoint: AiGatewayDestinationEndpointUpdate


    class azure.mgmt.aigateway.types.AiGatewayDestinationEndpoint(TypedDict, total=False):
        key "url": Required[str]
        url: str


    class azure.mgmt.aigateway.types.AiGatewayDestinationEndpointUpdate(TypedDict, total=False):
        key "url": str
        url: str


    class azure.mgmt.aigateway.types.AiGatewayEndpoint(TypedDict, total=False):
        key "api": str
        key "baseUrl": str
        key "url": Required[str]
        api: str
        baseUrl: str
        url: str


    class azure.mgmt.aigateway.types.AiGatewayFallbackTarget(TypedDict, total=False):
        key "modelId": Required[str]
        modelId: str


    class azure.mgmt.aigateway.types.AiGatewayFallbackTargetUpdate(TypedDict, total=False):
        key "modelId": str
        modelId: str


    class azure.mgmt.aigateway.types.AiGatewayFoundryProviderConfiguration(TypedDict, total=False):
        key "endpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        key "resourceIds": Required[list[str]]
        endpoint: AiGatewayDestinationEndpoint
        resourceIds: list[str]


    class azure.mgmt.aigateway.types.AiGatewayFoundryProviderConfigurationUpdate(TypedDict, total=False):
        key "endpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        endpoint: AiGatewayDestinationEndpointUpdate
        resourceIds: list[str]


    class azure.mgmt.aigateway.types.AiGatewayFrontend(TypedDict, total=False):
        key "defaultHostname": str
        defaultHostname: str


    class azure.mgmt.aigateway.types.AiGatewayGitHubAppAuthentication(TypedDict, total=False):
        key "appId": str
        key "installationId": str
        key "privateKey": str
        appId: str
        installationId: str
        privateKey: str


    class azure.mgmt.aigateway.types.AiGatewayManagedIdentityAuthentication(TypedDict, total=False):
        key "clientId": str
        key "resource": str
        clientId: str
        resource: str


    class azure.mgmt.aigateway.types.AiGatewayMcpUrlConfiguration(TypedDict, total=False):
        key "endpoint": Required[AiGatewayDestinationEndpoint]
        key "transport": Union[str, AiGatewayToolServerMcpTransport]
        endpoint: AiGatewayDestinationEndpoint
        transport: Union[str, AiGatewayToolServerMcpTransport]


    class azure.mgmt.aigateway.types.AiGatewayMcpUrlConfigurationUpdate(TypedDict, total=False):
        key "endpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        key "transport": Union[str, AiGatewayToolServerMcpTransport]
        endpoint: AiGatewayDestinationEndpointUpdate
        transport: Union[str, AiGatewayToolServerMcpTransport]


    class azure.mgmt.aigateway.types.AiGatewayModelDeployment(TypedDict, total=False):
        key "modelName": Required[str]
        key "modelVersion": str
        key "resourceId": str
        modelName: str
        modelVersion: str
        resourceId: str


    class azure.mgmt.aigateway.types.AiGatewayModelDeploymentUpdate(TypedDict, total=False):
        key "modelName": str
        key "modelVersion": str
        key "resourceId": str
        modelName: str
        modelVersion: str
        resourceId: str


    class azure.mgmt.aigateway.types.AiGatewayModelEndpoint(TypedDict, total=False):
        key "api": Required[str]
        key "path": Required[str]
        api: str
        path: str


    class azure.mgmt.aigateway.types.AiGatewayModelEndpointUpdate(TypedDict, total=False):
        key "api": str
        key "path": str
        api: str
        path: str


    class azure.mgmt.aigateway.types.AiGatewayModelProperties(TypedDict, total=False):
        key "deployment": Required[AiGatewayModelDeployment]
        key "description": str
        key "displayName": Required[str]
        key "providerKind": Union[str, AiGatewayModelProviderKind]
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        deployment: AiGatewayModelDeployment
        description: str
        displayName: str
        endpoints: list[AiGatewayModelEndpoint]
        policies: list[AiGatewayPolicy]
        providerKind: Union[str, AiGatewayModelProviderKind]
        provisioningState: Union[str, AiGatewayProvisioningState]
        supportedEndpoints: list[str]


    class azure.mgmt.aigateway.types.AiGatewayModelProviderAuthentication(TypedDict, total=False):
        key "githubApp": ForwardRef('AiGatewayGitHubAppAuthentication', module='types')
        key "managedIdentity": ForwardRef('AiGatewayManagedIdentityAuthentication', module='types')
        githubApp: AiGatewayGitHubAppAuthentication
        headers: list[AiGatewaySecretHeader]
        managedIdentity: AiGatewayManagedIdentityAuthentication


    class azure.mgmt.aigateway.types.AiGatewayModelProviderAuthenticationUpdate(TypedDict, total=False):
        key "githubApp": ForwardRef('AiGatewayGitHubAppAuthentication', module='types')
        key "managedIdentity": ForwardRef('AiGatewayManagedIdentityAuthentication', module='types')
        githubApp: AiGatewayGitHubAppAuthentication
        headers: list[AiGatewaySecretHeaderUpdate]
        managedIdentity: AiGatewayManagedIdentityAuthentication


    class azure.mgmt.aigateway.types.AiGatewayModelProviderProperties(TypedDict, total=False):
        key "authentication": ForwardRef('AiGatewayModelProviderAuthentication', module='types')
        key "custom": ForwardRef('AiGatewayCustomProviderConfiguration', module='types')
        key "description": str
        key "displayName": Required[str]
        key "foundry": ForwardRef('AiGatewayFoundryProviderConfiguration', module='types')
        key "modelProviderType": Required[Union[str, AiGatewayModelProviderKind]]
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        authentication: AiGatewayModelProviderAuthentication
        custom: AiGatewayCustomProviderConfiguration
        description: str
        displayName: str
        foundry: AiGatewayFoundryProviderConfiguration
        modelProviderType: Union[str, AiGatewayModelProviderKind]
        provisioningState: Union[str, AiGatewayProvisioningState]


    class azure.mgmt.aigateway.types.AiGatewayModelProviderResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AiGatewayModelProviderProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AiGatewayModelProviderProperties
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.AiGatewayModelProviderUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AiGatewayModelProviderUpdateProperties', module='types')
        properties: AiGatewayModelProviderUpdateProperties


    class azure.mgmt.aigateway.types.AiGatewayModelProviderUpdateProperties(TypedDict, total=False):
        key "authentication": ForwardRef('AiGatewayModelProviderAuthenticationUpdate', module='types')
        key "custom": ForwardRef('AiGatewayCustomProviderConfigurationUpdate', module='types')
        key "description": str
        key "displayName": str
        key "foundry": ForwardRef('AiGatewayFoundryProviderConfigurationUpdate', module='types')
        authentication: AiGatewayModelProviderAuthenticationUpdate
        custom: AiGatewayCustomProviderConfigurationUpdate
        description: str
        displayName: str
        foundry: AiGatewayFoundryProviderConfigurationUpdate


    class azure.mgmt.aigateway.types.AiGatewayModelResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AiGatewayModelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AiGatewayModelProperties
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.AiGatewayModelSelection(TypedDict, total=False):
        key "objective": Required[Union[str, AiGatewayModelSelectionObjective]]
        allowedRequestOverrides: list[Union[str, AiGatewayAllowedRequestOverride]]
        objective: Union[str, AiGatewayModelSelectionObjective]


    class azure.mgmt.aigateway.types.AiGatewayModelSelectionUpdate(TypedDict, total=False):
        key "objective": Union[str, AiGatewayModelSelectionObjective]
        allowedRequestOverrides: list[Union[str, AiGatewayAllowedRequestOverride]]
        objective: Union[str, AiGatewayModelSelectionObjective]


    class azure.mgmt.aigateway.types.AiGatewayModelUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AiGatewayModelUpdateProperties', module='types')
        properties: AiGatewayModelUpdateProperties


    class azure.mgmt.aigateway.types.AiGatewayModelUpdateProperties(TypedDict, total=False):
        key "deployment": ForwardRef('AiGatewayModelDeploymentUpdate', module='types')
        key "description": str
        key "displayName": str
        deployment: AiGatewayModelDeploymentUpdate
        description: str
        displayName: str
        endpoints: list[AiGatewayModelEndpointUpdate]
        policies: list[AiGatewayPolicyUpdate]
        supportedEndpoints: list[str]


    class azure.mgmt.aigateway.types.AiGatewayNameValuePair(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.aigateway.types.AiGatewayNameValuePairUpdate(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.aigateway.types.AiGatewayOpenApiConfiguration(TypedDict, total=False):
        key "specSource": Required[AiGatewayOpenApiSpecSource]
        specSource: AiGatewayOpenApiSpecSource


    class azure.mgmt.aigateway.types.AiGatewayOpenApiConfigurationUpdate(TypedDict, total=False):
        key "specSource": ForwardRef('AiGatewayOpenApiSpecSourceUpdate', module='types')
        specSource: AiGatewayOpenApiSpecSourceUpdate


    class azure.mgmt.aigateway.types.AiGatewayOpenApiSpecSource(TypedDict, total=False):
        key "contentBase64": str
        key "type": Required[Union[str, AiGatewayToolServerOpenApiSourceType]]
        key "url": str
        contentBase64: str
        type: Union[str, AiGatewayToolServerOpenApiSourceType]
        url: str


    class azure.mgmt.aigateway.types.AiGatewayOpenApiSpecSourceUpdate(TypedDict, total=False):
        key "contentBase64": str
        key "type": Union[str, AiGatewayToolServerOpenApiSourceType]
        key "url": str
        contentBase64: str
        type: Union[str, AiGatewayToolServerOpenApiSourceType]
        url: str


    class azure.mgmt.aigateway.types.AiGatewayOpenTelemetryConfiguration(TypedDict, total=False):
        key "logsEndpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        key "metricsEndpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        key "tracesEndpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        logsEndpoint: AiGatewayDestinationEndpoint
        metricsEndpoint: AiGatewayDestinationEndpoint
        tracesEndpoint: AiGatewayDestinationEndpoint


    class azure.mgmt.aigateway.types.AiGatewayOpenTelemetryConfigurationUpdate(TypedDict, total=False):
        key "logsEndpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        key "metricsEndpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        key "tracesEndpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        logsEndpoint: AiGatewayDestinationEndpointUpdate
        metricsEndpoint: AiGatewayDestinationEndpointUpdate
        tracesEndpoint: AiGatewayDestinationEndpointUpdate


    class azure.mgmt.aigateway.types.AiGatewayPolicy(TypedDict, total=False):
        key "action": Union[str, AiGatewayIpFilterAction]
        key "allowCredentials": bool
        key "amount": float
        key "authentication": ForwardRef('AiGatewayAgentHookAuthentication', module='types')
        key "count": int
        key "endpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        key "hateSeverity": Union[str, AiGatewayContentSafetySeverity]
        key "hooks": ForwardRef('AiGatewayAgentHooks', module='types')
        key "id": str
        key "mode": Union[str, AiGatewayFailureMode]
        key "period": Union[str, AiGatewayPolicyPeriod]
        key "postInvocation": bool
        key "preInvocation": bool
        key "preflightResultMaxAge": int
        key "scope": Union[str, AiGatewayPolicyScope]
        key "selfHarmSeverity": Union[str, AiGatewayContentSafetySeverity]
        key "sexualSeverity": Union[str, AiGatewayContentSafetySeverity]
        key "terminateUnmatchedRequest": bool
        key "threshold": int
        key "tripDurationSeconds": int
        key "type": Required[Union[str, AiGatewayPolicyType]]
        key "violenceSeverity": Union[str, AiGatewayContentSafetySeverity]
        action: Union[str, AiGatewayIpFilterAction]
        allowCredentials: bool
        allowedHeaders: list[str]
        allowedMethods: list[str]
        allowedOrigins: list[str]
        amount: float
        authentication: AiGatewayAgentHookAuthentication
        cidrRanges: list[str]
        count: int
        counterKey: list[Union[str, AiGatewayCounterDimension]]
        endpoint: AiGatewayDestinationEndpoint
        exposeHeaders: list[str]
        fallbackTargets: list[AiGatewayFallbackTarget]
        hateSeverity: Union[str, AiGatewayContentSafetySeverity]
        headers: list[AiGatewayNameValuePair]
        hooks: AiGatewayAgentHooks
        id: str
        mode: Union[str, AiGatewayFailureMode]
        overrides: list[AiGatewayCostLimitOverride]
        period: Union[str, AiGatewayPolicyPeriod]
        postInvocation: bool
        preInvocation: bool
        preflightResultMaxAge: int
        scope: Union[str, AiGatewayPolicyScope]
        selfHarmSeverity: Union[str, AiGatewayContentSafetySeverity]
        sexualSeverity: Union[str, AiGatewayContentSafetySeverity]
        terminateUnmatchedRequest: bool
        threshold: int
        tripDurationSeconds: int
        type: Union[str, AiGatewayPolicyType]
        violenceSeverity: Union[str, AiGatewayContentSafetySeverity]


    class azure.mgmt.aigateway.types.AiGatewayPolicyUpdate(TypedDict, total=False):
        key "action": Union[str, AiGatewayIpFilterAction]
        key "allowCredentials": bool
        key "amount": float
        key "authentication": ForwardRef('AiGatewayAgentHookAuthenticationUpdate', module='types')
        key "count": int
        key "endpoint": ForwardRef('AiGatewayDestinationEndpointUpdate', module='types')
        key "hateSeverity": Union[str, AiGatewayContentSafetySeverity]
        key "hooks": ForwardRef('AiGatewayAgentHooksUpdate', module='types')
        key "id": str
        key "mode": Union[str, AiGatewayFailureMode]
        key "period": Union[str, AiGatewayPolicyPeriod]
        key "postInvocation": bool
        key "preInvocation": bool
        key "preflightResultMaxAge": int
        key "scope": Union[str, AiGatewayPolicyScope]
        key "selfHarmSeverity": Union[str, AiGatewayContentSafetySeverity]
        key "sexualSeverity": Union[str, AiGatewayContentSafetySeverity]
        key "terminateUnmatchedRequest": bool
        key "threshold": int
        key "tripDurationSeconds": int
        key "type": Union[str, AiGatewayPolicyType]
        key "violenceSeverity": Union[str, AiGatewayContentSafetySeverity]
        action: Union[str, AiGatewayIpFilterAction]
        allowCredentials: bool
        allowedHeaders: list[str]
        allowedMethods: list[str]
        allowedOrigins: list[str]
        amount: float
        authentication: AiGatewayAgentHookAuthenticationUpdate
        cidrRanges: list[str]
        count: int
        counterKey: list[Union[str, AiGatewayCounterDimension]]
        endpoint: AiGatewayDestinationEndpointUpdate
        exposeHeaders: list[str]
        fallbackTargets: list[AiGatewayFallbackTargetUpdate]
        hateSeverity: Union[str, AiGatewayContentSafetySeverity]
        headers: list[AiGatewayNameValuePairUpdate]
        hooks: AiGatewayAgentHooksUpdate
        id: str
        mode: Union[str, AiGatewayFailureMode]
        overrides: list[AiGatewayCostLimitOverrideUpdate]
        period: Union[str, AiGatewayPolicyPeriod]
        postInvocation: bool
        preInvocation: bool
        preflightResultMaxAge: int
        scope: Union[str, AiGatewayPolicyScope]
        selfHarmSeverity: Union[str, AiGatewayContentSafetySeverity]
        sexualSeverity: Union[str, AiGatewayContentSafetySeverity]
        terminateUnmatchedRequest: bool
        threshold: int
        tripDurationSeconds: int
        type: Union[str, AiGatewayPolicyType]
        violenceSeverity: Union[str, AiGatewayContentSafetySeverity]


    class azure.mgmt.aigateway.types.AiGatewayPrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.AiGatewayProperties(TypedDict, total=False):
        key "backend": ForwardRef('AiGatewayBackend', module='types')
        key "frontend": ForwardRef('AiGatewayFrontend', module='types')
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        key "publicNetworkAccess": Union[str, AiGatewayPublicNetworkAccess]
        backend: AiGatewayBackend
        frontend: AiGatewayFrontend
        privateEndpointConnections: list[AiGatewayPrivateEndpointConnection]
        provisioningState: Union[str, AiGatewayProvisioningState]
        publicNetworkAccess: Union[str, AiGatewayPublicNetworkAccess]


    class azure.mgmt.aigateway.types.AiGatewayResource(TrackedResource):
        key "eTag": str
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[AiGatewayProperties]
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AiGatewayProperties
        sku: Sku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.aigateway.types.AiGatewaySecretHeader(TypedDict, total=False):
        key "name": Required[str]
        key "value": str
        name: str
        value: str


    class azure.mgmt.aigateway.types.AiGatewaySecretHeaderUpdate(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.aigateway.types.AiGatewaySessionBackendPreference(TypedDict, total=False):
        key "key": Required[str]
        key: str


    class azure.mgmt.aigateway.types.AiGatewaySessionBackendPreferenceUpdate(TypedDict, total=False):
        key "key": str
        key: str


    class azure.mgmt.aigateway.types.AiGatewaySkuUpdate(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": str
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.aigateway.types.AiGatewaySubnet(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.aigateway.types.AiGatewaySubnetUpdate(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.aigateway.types.AiGatewayTelemetryAttributeMapping(TypedDict, total=False):
        key "source": Required[AiGatewayTelemetryAttributeSource]
        signals: list[Union[str, AiGatewayTelemetrySignal]]
        source: AiGatewayTelemetryAttributeSource


    class azure.mgmt.aigateway.types.AiGatewayTelemetryAttributeMappingUpdate(TypedDict, total=False):
        key "source": ForwardRef('AiGatewayTelemetryAttributeSourceUpdate', module='types')
        signals: list[Union[str, AiGatewayTelemetrySignal]]
        source: AiGatewayTelemetryAttributeSourceUpdate


    class azure.mgmt.aigateway.types.AiGatewayTelemetryAttributeSource(TypedDict, total=False):
        key "kind": Required[Literal["claims"]]
        key "value": Required[str]
        kind: Literal[claims]
        value: str


    class azure.mgmt.aigateway.types.AiGatewayTelemetryAttributeSourceUpdate(TypedDict, total=False):
        key "kind": Literal["claims"]
        key "value": str
        kind: Literal[claims]
        value: str


    class azure.mgmt.aigateway.types.AiGatewayTelemetryAuthentication(TypedDict, total=False):
        key "managedIdentity": ForwardRef('AiGatewayTelemetryManagedIdentity', module='types')
        headers: list[AiGatewaySecretHeader]
        managedIdentity: AiGatewayTelemetryManagedIdentity


    class azure.mgmt.aigateway.types.AiGatewayTelemetryAuthenticationUpdate(TypedDict, total=False):
        key "managedIdentity": ForwardRef('AiGatewayTelemetryManagedIdentity', module='types')
        headers: list[AiGatewaySecretHeaderUpdate]
        managedIdentity: AiGatewayTelemetryManagedIdentity


    class azure.mgmt.aigateway.types.AiGatewayTelemetryConfiguration(TypedDict, total=False):
        attributes: list[AiGatewayTelemetryAttributeMapping]


    class azure.mgmt.aigateway.types.AiGatewayTelemetryConfigurationUpdate(TypedDict, total=False):
        attributes: list[AiGatewayTelemetryAttributeMappingUpdate]


    class azure.mgmt.aigateway.types.AiGatewayTelemetryExporterProperties(TypedDict, total=False):
        key "applicationInsights": ForwardRef('AiGatewayApplicationInsightsConfiguration', module='types')
        key "authentication": ForwardRef('AiGatewayTelemetryAuthentication', module='types')
        key "openTelemetry": ForwardRef('AiGatewayOpenTelemetryConfiguration', module='types')
        key "payloadCapture": bool
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        key "telemetry": ForwardRef('AiGatewayTelemetryConfiguration', module='types')
        key "telemetryExporterType": Required[Union[str, AiGatewayTelemetryExporterKind]]
        applicationInsights: AiGatewayApplicationInsightsConfiguration
        authentication: AiGatewayTelemetryAuthentication
        openTelemetry: AiGatewayOpenTelemetryConfiguration
        payloadCapture: bool
        provisioningState: Union[str, AiGatewayProvisioningState]
        telemetry: AiGatewayTelemetryConfiguration
        telemetryExporterType: Union[str, AiGatewayTelemetryExporterKind]


    class azure.mgmt.aigateway.types.AiGatewayTelemetryExporterResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AiGatewayTelemetryExporterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AiGatewayTelemetryExporterProperties
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.AiGatewayTelemetryExporterUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AiGatewayTelemetryExporterUpdateProperties', module='types')
        properties: AiGatewayTelemetryExporterUpdateProperties


    class azure.mgmt.aigateway.types.AiGatewayTelemetryExporterUpdateProperties(TypedDict, total=False):
        key "applicationInsights": ForwardRef('AiGatewayApplicationInsightsConfiguration', module='types')
        key "authentication": ForwardRef('AiGatewayTelemetryAuthenticationUpdate', module='types')
        key "openTelemetry": ForwardRef('AiGatewayOpenTelemetryConfigurationUpdate', module='types')
        key "payloadCapture": bool
        key "telemetry": ForwardRef('AiGatewayTelemetryConfigurationUpdate', module='types')
        applicationInsights: AiGatewayApplicationInsightsConfiguration
        authentication: AiGatewayTelemetryAuthenticationUpdate
        openTelemetry: AiGatewayOpenTelemetryConfigurationUpdate
        payloadCapture: bool
        telemetry: AiGatewayTelemetryConfigurationUpdate


    class azure.mgmt.aigateway.types.AiGatewayTelemetryManagedIdentity(TypedDict, total=False):
        key "clientId": str
        key "resource": str
        clientId: str
        resource: str


    class azure.mgmt.aigateway.types.AiGatewayToolServerAuthentication(TypedDict, total=False):
        key "managedIdentity": ForwardRef('AiGatewayToolServerManagedIdentityAuthentication', module='types')
        key "oauth2": ForwardRef('AiGatewayToolServerOauth2Authentication', module='types')
        headers: list[AiGatewaySecretHeader]
        managedIdentity: AiGatewayToolServerManagedIdentityAuthentication
        oauth2: AiGatewayToolServerOauth2Authentication


    class azure.mgmt.aigateway.types.AiGatewayToolServerAuthenticationUpdate(TypedDict, total=False):
        key "managedIdentity": ForwardRef('AiGatewayToolServerManagedIdentityAuthentication', module='types')
        key "oauth2": ForwardRef('AiGatewayToolServerOauth2Authentication', module='types')
        headers: list[AiGatewaySecretHeaderUpdate]
        managedIdentity: AiGatewayToolServerManagedIdentityAuthentication
        oauth2: AiGatewayToolServerOauth2Authentication


    class azure.mgmt.aigateway.types.AiGatewayToolServerEndpoint(TypedDict, total=False):
        key "authentication": ForwardRef('AiGatewayToolServerAuthentication', module='types')
        key "id": str
        key "kind": Required[Union[str, AiGatewayToolServerEndpointSourceKind]]
        key "mcp": ForwardRef('AiGatewayMcpUrlConfiguration', module='types')
        key "mode": Union[str, AiGatewayFailureMode]
        key "namespace": str
        key "openApi": ForwardRef('AiGatewayOpenApiConfiguration', module='types')
        authentication: AiGatewayToolServerAuthentication
        id: str
        kind: Union[str, AiGatewayToolServerEndpointSourceKind]
        mcp: AiGatewayMcpUrlConfiguration
        mode: Union[str, AiGatewayFailureMode]
        namespace: str
        openApi: AiGatewayOpenApiConfiguration
        tools: list[str]


    class azure.mgmt.aigateway.types.AiGatewayToolServerEndpointUpdate(TypedDict, total=False):
        key "authentication": ForwardRef('AiGatewayToolServerAuthenticationUpdate', module='types')
        key "id": str
        key "kind": Union[str, AiGatewayToolServerEndpointSourceKind]
        key "mcp": ForwardRef('AiGatewayMcpUrlConfigurationUpdate', module='types')
        key "mode": Union[str, AiGatewayFailureMode]
        key "namespace": str
        key "openApi": ForwardRef('AiGatewayOpenApiConfigurationUpdate', module='types')
        authentication: AiGatewayToolServerAuthenticationUpdate
        id: str
        kind: Union[str, AiGatewayToolServerEndpointSourceKind]
        mcp: AiGatewayMcpUrlConfigurationUpdate
        mode: Union[str, AiGatewayFailureMode]
        namespace: str
        openApi: AiGatewayOpenApiConfigurationUpdate
        tools: list[str]


    class azure.mgmt.aigateway.types.AiGatewayToolServerFederation(TypedDict, total=False):
        key "appCredential": ForwardRef('AiGatewayToolServerFederationAppCredential', module='types')
        key "applicationId": str
        appCredential: AiGatewayToolServerFederationAppCredential
        applicationId: str


    class azure.mgmt.aigateway.types.AiGatewayToolServerFederationAppCredential(TypedDict, total=False):
        key "clientId": str
        key "type": Required[Union[str, AiGatewayToolServerFederationAppCredentialType]]
        clientId: str
        type: Union[str, AiGatewayToolServerFederationAppCredentialType]


    class azure.mgmt.aigateway.types.AiGatewayToolServerLoginLinksRequest(TypedDict, total=False):
        key "endpointId": Required[str]
        endpointId: str


    class azure.mgmt.aigateway.types.AiGatewayToolServerManagedIdentityAuthentication(TypedDict, total=False):
        key "clientId": str
        key "resource": str
        clientId: str
        resource: str


    class azure.mgmt.aigateway.types.AiGatewayToolServerOauth2Authentication(TypedDict, total=False):
        key "authorizationEndpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        key "clientId": str
        key "clientSecret": str
        key "grantType": Union[str, AiGatewayToolServerOauth2GrantType]
        key "issuer": str
        key "loginLink": str
        key "status": str
        key "statusUpdatedUtc": str
        key "tokenEndpoint": ForwardRef('AiGatewayDestinationEndpoint', module='types')
        key "tokenExchange": ForwardRef('AiGatewayToolServerTokenExchange', module='types')
        authorizationEndpoint: AiGatewayDestinationEndpoint
        authorizationParameters: list[AiGatewayToolServerOauth2Parameter]
        clientId: str
        clientSecret: str
        grantType: Union[str, AiGatewayToolServerOauth2GrantType]
        issuer: str
        loginLink: str
        scopes: list[str]
        status: str
        statusUpdatedUtc: str
        tokenEndpoint: AiGatewayDestinationEndpoint
        tokenExchange: AiGatewayToolServerTokenExchange
        tokenParameters: list[AiGatewayToolServerOauth2Parameter]


    class azure.mgmt.aigateway.types.AiGatewayToolServerOauth2Parameter(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.aigateway.types.AiGatewayToolServerProperties(TypedDict, total=False):
        key "accessState": Union[str, AiGatewayToolServerAccessState]
        key "description": str
        key "displayName": str
        key "path": str
        key "provisioningState": Union[str, AiGatewayProvisioningState]
        key "subscriptionRequired": bool
        key "toolServerType": Required[Union[str, AiGatewayToolServerType]]
        accessState: Union[str, AiGatewayToolServerAccessState]
        allowList: list[str]
        blockList: list[str]
        description: str
        displayName: str
        endpoints: list[AiGatewayToolServerEndpoint]
        gatewayEndpoints: list[AiGatewayEndpoint]
        path: str
        policies: list[AiGatewayPolicy]
        provisioningState: Union[str, AiGatewayProvisioningState]
        subscriptionRequired: bool
        toolServerType: Union[str, AiGatewayToolServerType]
        versions: list[str]


    class azure.mgmt.aigateway.types.AiGatewayToolServerResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AiGatewayToolServerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AiGatewayToolServerProperties
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.AiGatewayToolServerTokenExchange(TypedDict, total=False):
        key "federatedClientApplication": ForwardRef('AiGatewayToolServerFederation', module='types')
        key "profile": Required[Union[str, AiGatewayToolServerTokenExchangeProfile]]
        federatedClientApplication: AiGatewayToolServerFederation
        profile: Union[str, AiGatewayToolServerTokenExchangeProfile]
        scopes: list[str]


    class azure.mgmt.aigateway.types.AiGatewayToolServerUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AiGatewayToolServerUpdateProperties', module='types')
        properties: AiGatewayToolServerUpdateProperties


    class azure.mgmt.aigateway.types.AiGatewayToolServerUpdateProperties(TypedDict, total=False):
        key "accessState": Union[str, AiGatewayToolServerAccessState]
        key "description": str
        key "displayName": str
        key "path": str
        key "subscriptionRequired": bool
        key "toolServerType": Union[str, AiGatewayToolServerType]
        accessState: Union[str, AiGatewayToolServerAccessState]
        allowList: list[str]
        blockList: list[str]
        description: str
        displayName: str
        endpoints: list[AiGatewayToolServerEndpointUpdate]
        path: str
        policies: list[AiGatewayPolicyUpdate]
        subscriptionRequired: bool
        toolServerType: Union[str, AiGatewayToolServerType]
        versions: list[str]


    class azure.mgmt.aigateway.types.AiGatewayUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('AiGatewayUpdateProperties', module='types')
        key "sku": ForwardRef('AiGatewaySkuUpdate', module='types')
        identity: ManagedServiceIdentity
        properties: AiGatewayUpdateProperties
        sku: AiGatewaySkuUpdate
        tags: dict[str, str]


    class azure.mgmt.aigateway.types.AiGatewayUpdateProperties(TypedDict, total=False):
        key "backend": ForwardRef('AiGatewayBackendUpdate', module='types')
        key "publicNetworkAccess": Union[str, AiGatewayPublicNetworkAccess]
        backend: AiGatewayBackendUpdate
        publicNetworkAccess: Union[str, AiGatewayPublicNetworkAccess]


    class azure.mgmt.aigateway.types.AiGatewayWorkspaceUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AiGatewayWorkspaceUpdateProperties', module='types')
        properties: AiGatewayWorkspaceUpdateProperties


    class azure.mgmt.aigateway.types.AiGatewayWorkspaceUpdateProperties(TypedDict, total=False):
        policies: list[AiGatewayPolicyUpdate]


    class azure.mgmt.aigateway.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.aigateway.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.aigateway.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.aigateway.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.aigateway.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.aigateway.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.aigateway.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.aigateway.types.TrackedResource(Resource):
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


    class azure.mgmt.aigateway.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```