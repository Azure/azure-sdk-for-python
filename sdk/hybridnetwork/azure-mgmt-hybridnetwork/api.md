```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.hybridnetwork

    class azure.mgmt.hybridnetwork.HybridNetworkManagementClient: implements ContextManager 
        artifact_manifests: ArtifactManifestsOperations
        artifact_stores: ArtifactStoresOperations
        components: ComponentsOperations
        configuration_group_schemas: ConfigurationGroupSchemasOperations
        configuration_group_values: ConfigurationGroupValuesOperations
        network_function_definition_groups: NetworkFunctionDefinitionGroupsOperations
        network_function_definition_versions: NetworkFunctionDefinitionVersionsOperations
        network_functions: NetworkFunctionsOperations
        network_service_design_groups: NetworkServiceDesignGroupsOperations
        network_service_design_versions: NetworkServiceDesignVersionsOperations
        operations: Operations
        proxy_artifact: ProxyArtifactOperations
        publishers: PublishersOperations
        site_network_services: SiteNetworkServicesOperations
        sites: SitesOperations

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


namespace azure.mgmt.hybridnetwork.aio

    class azure.mgmt.hybridnetwork.aio.HybridNetworkManagementClient: implements AsyncContextManager 
        artifact_manifests: ArtifactManifestsOperations
        artifact_stores: ArtifactStoresOperations
        components: ComponentsOperations
        configuration_group_schemas: ConfigurationGroupSchemasOperations
        configuration_group_values: ConfigurationGroupValuesOperations
        network_function_definition_groups: NetworkFunctionDefinitionGroupsOperations
        network_function_definition_versions: NetworkFunctionDefinitionVersionsOperations
        network_functions: NetworkFunctionsOperations
        network_service_design_groups: NetworkServiceDesignGroupsOperations
        network_service_design_versions: NetworkServiceDesignVersionsOperations
        operations: Operations
        proxy_artifact: ProxyArtifactOperations
        publishers: PublishersOperations
        site_network_services: SiteNetworkServicesOperations
        sites: SitesOperations

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


namespace azure.mgmt.hybridnetwork.aio.operations

    class azure.mgmt.hybridnetwork.aio.operations.ArtifactManifestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: ArtifactManifest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArtifactManifest]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArtifactManifest]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: ArtifactManifestUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArtifactManifestUpdateState]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArtifactManifestUpdateState]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactManifest: ...

        @distributed_trace
        def list_by_artifact_store(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ArtifactManifest]: ...

        @distributed_trace_async
        async def list_credential(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactAccessCredential: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactManifest: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactManifest: ...


    class azure.mgmt.hybridnetwork.aio.operations.ArtifactStoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: ArtifactStore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArtifactStore]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArtifactStore]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactStore: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ArtifactStore]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactStore: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactStore: ...


    class azure.mgmt.hybridnetwork.aio.operations.ComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                component_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Component: ...

        @distributed_trace
        def list_by_network_function(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Component]: ...


    class azure.mgmt.hybridnetwork.aio.operations.ConfigurationGroupSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: ConfigurationGroupSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationGroupSchema]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationGroupSchema]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: ConfigurationGroupSchemaVersionUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationGroupSchemaVersionUpdateState]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationGroupSchemaVersionUpdateState]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationGroupSchema: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationGroupSchema]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupSchema: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupSchema: ...


    class azure.mgmt.hybridnetwork.aio.operations.ConfigurationGroupValuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: ConfigurationGroupValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationGroupValue]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ConfigurationGroupValue]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationGroupValue: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationGroupValue]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationGroupValue]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupValue: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupValue: ...


    class azure.mgmt.hybridnetwork.aio.operations.NetworkFunctionDefinitionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: NetworkFunctionDefinitionGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunctionDefinitionGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunctionDefinitionGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionGroup: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFunctionDefinitionGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionGroup: ...


    class azure.mgmt.hybridnetwork.aio.operations.NetworkFunctionDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: NetworkFunctionDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunctionDefinitionVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunctionDefinitionVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: NetworkFunctionDefinitionVersionUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunctionDefinitionVersionUpdateState]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunctionDefinitionVersionUpdateState]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionVersion: ...

        @distributed_trace
        def list_by_network_function_definition_group(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFunctionDefinitionVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionVersion: ...


    class azure.mgmt.hybridnetwork.aio.operations.NetworkFunctionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: NetworkFunction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunction]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkFunction]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute_request(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: ExecuteRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute_request(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFunction: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFunction]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkFunction]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunction: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunction: ...


    class azure.mgmt.hybridnetwork.aio.operations.NetworkServiceDesignGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: NetworkServiceDesignGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkServiceDesignGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkServiceDesignGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkServiceDesignGroup: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkServiceDesignGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignGroup: ...


    class azure.mgmt.hybridnetwork.aio.operations.NetworkServiceDesignVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: NetworkServiceDesignVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkServiceDesignVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkServiceDesignVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: NetworkServiceDesignVersionUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkServiceDesignVersionUpdateState]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkServiceDesignVersionUpdateState]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkServiceDesignVersion: ...

        @distributed_trace
        def list_by_network_service_design_group(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[NetworkServiceDesignVersion]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignVersion: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignVersion: ...


    class azure.mgmt.hybridnetwork.aio.operations.Operations:

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


    class azure.mgmt.hybridnetwork.aio.operations.ProxyArtifactOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_name: str, 
                artifact_version_name: str, 
                parameters: ArtifactChangeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProxyArtifactVersionsListOverview]: ...

        @overload
        async def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_name: str, 
                artifact_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProxyArtifactVersionsListOverview]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ProxyArtifactVersionsListOverview]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ProxyArtifactListOverview]: ...


    class azure.mgmt.hybridnetwork.aio.operations.PublishersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[Publisher] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Publisher]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Publisher]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Publisher: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Publisher]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Publisher]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[TagsObject] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Publisher: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Publisher: ...


    class azure.mgmt.hybridnetwork.aio.operations.SiteNetworkServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: SiteNetworkService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteNetworkService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SiteNetworkService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SiteNetworkService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SiteNetworkService]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SiteNetworkService]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteNetworkService: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteNetworkService: ...


    class azure.mgmt.hybridnetwork.aio.operations.SitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Site]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                site_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                site_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Site]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Site]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


namespace azure.mgmt.hybridnetwork.models

    class azure.mgmt.hybridnetwork.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.hybridnetwork.models.ApplicationEnablement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ArmResourceDefinitionResourceElementTemplate(Model):
        artifact_profile: NSDArtifactProfile
        parameter_values: str
        template_type: Union[str, TemplateType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_profile: Optional[NSDArtifactProfile] = ..., 
                parameter_values: Optional[str] = ..., 
                template_type: Optional[Union[str, TemplateType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArmResourceDefinitionResourceElementTemplateDetails(ResourceElementTemplate):
        configuration: ArmResourceDefinitionResourceElementTemplate
        depends_on_profile: DependsOnProfile
        name: str
        resource_element_type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ArmResourceDefinitionResourceElementTemplate] = ..., 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.ArmTemplateArtifactProfile(Model):
        template_name: str
        template_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                template_name: Optional[str] = ..., 
                template_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArmTemplateMappingRuleProfile(Model):
        template_parameters: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                template_parameters: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactAccessCredential(Model):
        credential_type: Union[str, CredentialType]

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


    class azure.mgmt.hybridnetwork.models.ArtifactChangeState(Model):
        properties: ArtifactChangeStateProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ArtifactChangeStateProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactChangeStateProperties(Model):
        artifact_state: Union[str, ArtifactState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_state: Optional[Union[str, ArtifactState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactManifest(TrackedResource):
        id: str
        location: str
        name: str
        properties: ArtifactManifestPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ArtifactManifestPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.ArtifactManifestListResult(Model):
        next_link: str
        value: list[ArtifactManifest]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ArtifactManifest]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactManifestPropertiesFormat(Model):
        artifact_manifest_state: Union[str, ArtifactManifestState]
        artifacts: list[ManifestArtifactFormat]
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifacts: Optional[List[ManifestArtifactFormat]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactManifestState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPLOADED = "Uploaded"
        UPLOADING = "Uploading"
        VALIDATING = "Validating"
        VALIDATION_FAILED = "ValidationFailed"


    class azure.mgmt.hybridnetwork.models.ArtifactManifestUpdateState(Model):
        artifact_manifest_state: Union[str, ArtifactManifestState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_manifest_state: Optional[Union[str, ArtifactManifestState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactProfile(Model):
        artifact_store: ReferencedResource

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_store: Optional[ReferencedResource] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactReplicationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SINGLE_REPLICATION = "SingleReplication"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ArtifactState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DEPRECATED = "Deprecated"
        PREVIEW = "Preview"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ArtifactStore(TrackedResource):
        id: str
        location: str
        name: str
        properties: ArtifactStorePropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ArtifactStorePropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.ArtifactStoreListResult(Model):
        next_link: str
        value: list[ArtifactStore]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ArtifactStore]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactStorePropertiesFormat(Model):
        managed_resource_group_configuration: ArtifactStorePropertiesFormatManagedResourceGroupConfiguration
        provisioning_state: Union[str, ProvisioningState]
        replication_strategy: Union[str, ArtifactReplicationStrategy]
        storage_resource_id: str
        store_type: Union[str, ArtifactStoreType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_resource_group_configuration: Optional[ArtifactStorePropertiesFormatManagedResourceGroupConfiguration] = ..., 
                replication_strategy: Optional[Union[str, ArtifactReplicationStrategy]] = ..., 
                store_type: Optional[Union[str, ArtifactStoreType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ArtifactStorePropertiesFormatManagedResourceGroupConfiguration(Model):
        location: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
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


    class azure.mgmt.hybridnetwork.models.ArtifactStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CONTAINER_REGISTRY = "AzureContainerRegistry"
        AZURE_STORAGE_ACCOUNT = "AzureStorageAccount"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ArtifactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM_TEMPLATE = "ArmTemplate"
        IMAGE_FILE = "ImageFile"
        OCI_ARTIFACT = "OCIArtifact"
        UNKNOWN = "Unknown"
        VHD_IMAGE_FILE = "VhdImageFile"


    class azure.mgmt.hybridnetwork.models.AzureArcK8SClusterNFVIDetails(NFVIs):
        custom_location_reference: ReferencedResource
        name: str
        nfvi_type: Union[str, NFVIType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_location_reference: Optional[ReferencedResource] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureArcKubernetesArtifactProfile(ArtifactProfile):
        artifact_store: ReferencedResource
        helm_artifact_profile: HelmArtifactProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_store: Optional[ReferencedResource] = ..., 
                helm_artifact_profile: Optional[HelmArtifactProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureArcKubernetesArtifactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HELM_PACKAGE = "HelmPackage"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.AzureArcKubernetesDeployMappingRuleProfile(MappingRuleProfile):
        application_enablement: Union[str, ApplicationEnablement]
        helm_mapping_rule_profile: HelmMappingRuleProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_enablement: Optional[Union[str, ApplicationEnablement]] = ..., 
                helm_mapping_rule_profile: Optional[HelmMappingRuleProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureArcKubernetesHelmApplication(AzureArcKubernetesNetworkFunctionApplication):
        artifact_profile: AzureArcKubernetesArtifactProfile
        artifact_type: Union[str, AzureArcKubernetesArtifactType]
        depends_on_profile: DependsOnProfile
        deploy_parameters_mapping_rule_profile: AzureArcKubernetesDeployMappingRuleProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_profile: Optional[AzureArcKubernetesArtifactProfile] = ..., 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
                deploy_parameters_mapping_rule_profile: Optional[AzureArcKubernetesDeployMappingRuleProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureArcKubernetesNetworkFunctionApplication(NetworkFunctionApplication):
        artifact_type: Union[str, AzureArcKubernetesArtifactType]
        depends_on_profile: DependsOnProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureArcKubernetesNetworkFunctionTemplate(ContainerizedNetworkFunctionTemplate):
        network_function_applications: list[AzureArcKubernetesNetworkFunctionApplication]
        nfvi_type: Union[str, ContainerizedNetworkFunctionNFVIType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_function_applications: Optional[List[AzureArcKubernetesNetworkFunctionApplication]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureContainerRegistryScopedTokenCredential(ArtifactAccessCredential):
        acr_server_url: str
        acr_token: str
        credential_type: Union[str, CredentialType]
        expiry: datetime
        repositories: list[str]
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                acr_server_url: Optional[str] = ..., 
                acr_token: Optional[str] = ..., 
                expiry: Optional[datetime] = ..., 
                repositories: Optional[List[str]] = ..., 
                username: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureCoreArmTemplateArtifactProfile(ArtifactProfile):
        artifact_store: ReferencedResource
        template_artifact_profile: ArmTemplateArtifactProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_store: Optional[ReferencedResource] = ..., 
                template_artifact_profile: Optional[ArmTemplateArtifactProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureCoreArmTemplateDeployMappingRuleProfile(MappingRuleProfile):
        application_enablement: Union[str, ApplicationEnablement]
        template_mapping_rule_profile: ArmTemplateMappingRuleProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_enablement: Optional[Union[str, ApplicationEnablement]] = ..., 
                template_mapping_rule_profile: Optional[ArmTemplateMappingRuleProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureCoreArtifactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM_TEMPLATE = "ArmTemplate"
        UNKNOWN = "Unknown"
        VHD_IMAGE_FILE = "VhdImageFile"


    class azure.mgmt.hybridnetwork.models.AzureCoreNFVIDetails(NFVIs):
        location: str
        name: str
        nfvi_type: Union[str, NFVIType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureCoreNetworkFunctionApplication(NetworkFunctionApplication):
        artifact_type: Union[str, AzureCoreArtifactType]
        depends_on_profile: DependsOnProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureCoreNetworkFunctionArmTemplateApplication(AzureCoreNetworkFunctionApplication):
        artifact_profile: AzureCoreArmTemplateArtifactProfile
        artifact_type: Union[str, AzureCoreArtifactType]
        depends_on_profile: DependsOnProfile
        deploy_parameters_mapping_rule_profile: AzureCoreArmTemplateDeployMappingRuleProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_profile: Optional[AzureCoreArmTemplateArtifactProfile] = ..., 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
                deploy_parameters_mapping_rule_profile: Optional[AzureCoreArmTemplateDeployMappingRuleProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureCoreNetworkFunctionTemplate(VirtualNetworkFunctionTemplate):
        network_function_applications: list[AzureCoreNetworkFunctionApplication]
        nfvi_type: Union[str, VirtualNetworkFunctionNFVIType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_function_applications: Optional[List[AzureCoreNetworkFunctionApplication]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureCoreNetworkFunctionVhdApplication(AzureCoreNetworkFunctionApplication):
        artifact_profile: AzureCoreVhdImageArtifactProfile
        artifact_type: Union[str, AzureCoreArtifactType]
        depends_on_profile: DependsOnProfile
        deploy_parameters_mapping_rule_profile: AzureCoreVhdImageDeployMappingRuleProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_profile: Optional[AzureCoreVhdImageArtifactProfile] = ..., 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
                deploy_parameters_mapping_rule_profile: Optional[AzureCoreVhdImageDeployMappingRuleProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureCoreVhdImageArtifactProfile(ArtifactProfile):
        artifact_store: ReferencedResource
        vhd_artifact_profile: VhdImageArtifactProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_store: Optional[ReferencedResource] = ..., 
                vhd_artifact_profile: Optional[VhdImageArtifactProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureCoreVhdImageDeployMappingRuleProfile(MappingRuleProfile):
        application_enablement: Union[str, ApplicationEnablement]
        vhd_image_mapping_rule_profile: VhdImageMappingRuleProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_enablement: Optional[Union[str, ApplicationEnablement]] = ..., 
                vhd_image_mapping_rule_profile: Optional[VhdImageMappingRuleProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusArmTemplateArtifactProfile(ArtifactProfile):
        artifact_store: ReferencedResource
        template_artifact_profile: ArmTemplateArtifactProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_store: Optional[ReferencedResource] = ..., 
                template_artifact_profile: Optional[ArmTemplateArtifactProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusArmTemplateDeployMappingRuleProfile(MappingRuleProfile):
        application_enablement: Union[str, ApplicationEnablement]
        template_mapping_rule_profile: ArmTemplateMappingRuleProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_enablement: Optional[Union[str, ApplicationEnablement]] = ..., 
                template_mapping_rule_profile: Optional[ArmTemplateMappingRuleProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusArtifactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM_TEMPLATE = "ArmTemplate"
        IMAGE_FILE = "ImageFile"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusClusterNFVIDetails(NFVIs):
        custom_location_reference: ReferencedResource
        name: str
        nfvi_type: Union[str, NFVIType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_location_reference: Optional[ReferencedResource] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusImageArtifactProfile(ArtifactProfile):
        artifact_store: ReferencedResource
        image_artifact_profile: ImageArtifactProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_store: Optional[ReferencedResource] = ..., 
                image_artifact_profile: Optional[ImageArtifactProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusImageDeployMappingRuleProfile(MappingRuleProfile):
        application_enablement: Union[str, ApplicationEnablement]
        image_mapping_rule_profile: ImageMappingRuleProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_enablement: Optional[Union[str, ApplicationEnablement]] = ..., 
                image_mapping_rule_profile: Optional[ImageMappingRuleProfile] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusNetworkFunctionApplication(NetworkFunctionApplication):
        artifact_type: Union[str, AzureOperatorNexusArtifactType]
        depends_on_profile: DependsOnProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusNetworkFunctionArmTemplateApplication(AzureOperatorNexusNetworkFunctionApplication):
        artifact_profile: AzureOperatorNexusArmTemplateArtifactProfile
        artifact_type: Union[str, AzureOperatorNexusArtifactType]
        depends_on_profile: DependsOnProfile
        deploy_parameters_mapping_rule_profile: AzureOperatorNexusArmTemplateDeployMappingRuleProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_profile: Optional[AzureOperatorNexusArmTemplateArtifactProfile] = ..., 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
                deploy_parameters_mapping_rule_profile: Optional[AzureOperatorNexusArmTemplateDeployMappingRuleProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusNetworkFunctionImageApplication(AzureOperatorNexusNetworkFunctionApplication):
        artifact_profile: AzureOperatorNexusImageArtifactProfile
        artifact_type: Union[str, AzureOperatorNexusArtifactType]
        depends_on_profile: DependsOnProfile
        deploy_parameters_mapping_rule_profile: AzureOperatorNexusImageDeployMappingRuleProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_profile: Optional[AzureOperatorNexusImageArtifactProfile] = ..., 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
                deploy_parameters_mapping_rule_profile: Optional[AzureOperatorNexusImageDeployMappingRuleProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.AzureOperatorNexusNetworkFunctionTemplate(VirtualNetworkFunctionTemplate):
        network_function_applications: list[AzureOperatorNexusNetworkFunctionApplication]
        nfvi_type: Union[str, VirtualNetworkFunctionNFVIType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_function_applications: Optional[List[AzureOperatorNexusNetworkFunctionApplication]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureStorageAccountContainerCredential(Model):
        container_name: str
        container_sas_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_name: Optional[str] = ..., 
                container_sas_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.AzureStorageAccountCredential(ArtifactAccessCredential):
        container_credentials: list[AzureStorageAccountContainerCredential]
        credential_type: Union[str, CredentialType]
        expiry: datetime
        storage_account_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                container_credentials: Optional[List[AzureStorageAccountContainerCredential]] = ..., 
                expiry: Optional[datetime] = ..., 
                storage_account_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.Component(ProxyResource):
        id: str
        name: str
        properties: ComponentProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ComponentProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ComponentListResult(Model):
        next_link: str
        value: list[Component]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Component]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ComponentProperties(Model):
        deployment_profile: str
        deployment_status: DeploymentStatusProperties
        provisioning_state: Union[str, ProvisioningState]

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


    class azure.mgmt.hybridnetwork.models.ConfigurationGenerationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HANDLEBAR_TEMPLATE = "HandlebarTemplate"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupSchema(TrackedResource):
        id: str
        location: str
        name: str
        properties: ConfigurationGroupSchemaPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ConfigurationGroupSchemaPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupSchemaListResult(Model):
        next_link: str
        value: list[ConfigurationGroupSchema]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ConfigurationGroupSchema]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupSchemaPropertiesFormat(Model):
        description: str
        provisioning_state: Union[str, ProvisioningState]
        schema_definition: str
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                schema_definition: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupSchemaVersionUpdateState(Model):
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                version_state: Optional[Union[str, VersionState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupValue(TrackedResource):
        id: str
        location: str
        name: str
        properties: ConfigurationGroupValuePropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ConfigurationGroupValuePropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupValueConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN = "Open"
        SECRET = "Secret"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupValueListResult(Model):
        next_link: str
        value: list[ConfigurationGroupValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ConfigurationGroupValue]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ConfigurationGroupValuePropertiesFormat(Model):
        configuration_group_schema_name: str
        configuration_group_schema_offering_location: str
        configuration_group_schema_resource_reference: DeploymentResourceIdReference
        configuration_type: Union[str, ConfigurationGroupValueConfigurationType]
        provisioning_state: Union[str, ProvisioningState]
        publisher_name: str
        publisher_scope: Union[str, PublisherScope]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_group_schema_resource_reference: Optional[DeploymentResourceIdReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ConfigurationValueWithSecrets(ConfigurationGroupValuePropertiesFormat):
        configuration_group_schema_name: str
        configuration_group_schema_offering_location: str
        configuration_group_schema_resource_reference: DeploymentResourceIdReference
        configuration_type: Union[str, ConfigurationGroupValueConfigurationType]
        provisioning_state: Union[str, ProvisioningState]
        publisher_name: str
        publisher_scope: Union[str, PublisherScope]
        secret_configuration_value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_group_schema_resource_reference: Optional[DeploymentResourceIdReference] = ..., 
                secret_configuration_value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ConfigurationValueWithoutSecrets(ConfigurationGroupValuePropertiesFormat):
        configuration_group_schema_name: str
        configuration_group_schema_offering_location: str
        configuration_group_schema_resource_reference: DeploymentResourceIdReference
        configuration_type: Union[str, ConfigurationGroupValueConfigurationType]
        configuration_value: str
        provisioning_state: Union[str, ProvisioningState]
        publisher_name: str
        publisher_scope: Union[str, PublisherScope]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_group_schema_resource_reference: Optional[DeploymentResourceIdReference] = ..., 
                configuration_value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ContainerizedNetworkFunctionDefinitionVersion(NetworkFunctionDefinitionVersionPropertiesFormat):
        deploy_parameters: str
        description: str
        network_function_template: ContainerizedNetworkFunctionTemplate
        network_function_type: Union[str, NetworkFunctionType]
        provisioning_state: Union[str, ProvisioningState]
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deploy_parameters: Optional[str] = ..., 
                description: Optional[str] = ..., 
                network_function_template: Optional[ContainerizedNetworkFunctionTemplate] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ContainerizedNetworkFunctionNFVIType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ARC_KUBERNETES = "AzureArcKubernetes"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ContainerizedNetworkFunctionTemplate(Model):
        nfvi_type: Union[str, ContainerizedNetworkFunctionNFVIType]

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


    class azure.mgmt.hybridnetwork.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.hybridnetwork.models.CredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CONTAINER_REGISTRY_SCOPED_TOKEN = "AzureContainerRegistryScopedToken"
        AZURE_STORAGE_ACCOUNT_TOKEN = "AzureStorageAccountToken"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.CustomLocationResourceId(Model):
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


    class azure.mgmt.hybridnetwork.models.DaemonSet(Model):
        available: int
        creation_time: datetime
        current: int
        desired: int
        name: str
        namespace: str
        ready: int
        up_to_date: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                available: Optional[int] = ..., 
                creation_time: Optional[datetime] = ..., 
                current: Optional[int] = ..., 
                desired: Optional[int] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                ready: Optional[int] = ..., 
                up_to_date: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.DependsOnProfile(Model):
        install_depends_on: list[str]
        uninstall_depends_on: list[str]
        update_depends_on: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                install_depends_on: Optional[List[str]] = ..., 
                uninstall_depends_on: Optional[List[str]] = ..., 
                update_depends_on: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.Deployment(Model):
        available: int
        creation_time: datetime
        desired: int
        name: str
        namespace: str
        ready: int
        up_to_date: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                available: Optional[int] = ..., 
                creation_time: Optional[datetime] = ..., 
                desired: Optional[int] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                ready: Optional[int] = ..., 
                up_to_date: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.DeploymentResourceIdReference(Model):
        id_type: Union[str, IdType]

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


    class azure.mgmt.hybridnetwork.models.DeploymentStatusProperties(Model):
        next_expected_update_at: datetime
        resources: Resources
        status: Union[str, Status]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_expected_update_at: Optional[datetime] = ..., 
                resources: Optional[Resources] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.hybridnetwork.models.ErrorDetail(Model):
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


    class azure.mgmt.hybridnetwork.models.ErrorResponse(Model):
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


    class azure.mgmt.hybridnetwork.models.ExecuteRequestParameters(Model):
        request_metadata: RequestMetadata
        service_endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                request_metadata: RequestMetadata, 
                service_endpoint: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.HelmArtifactProfile(Model):
        helm_package_name: str
        helm_package_version_range: str
        image_pull_secrets_values_paths: list[str]
        registry_values_paths: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                helm_package_name: Optional[str] = ..., 
                helm_package_version_range: Optional[str] = ..., 
                image_pull_secrets_values_paths: Optional[List[str]] = ..., 
                registry_values_paths: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.HelmInstallOptions(Model):
        atomic: str
        timeout: str
        wait: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                atomic: Optional[str] = ..., 
                timeout: Optional[str] = ..., 
                wait: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.HelmMappingRuleProfile(Model):
        helm_package_version: str
        options: HelmMappingRuleProfileOptions
        release_name: str
        release_namespace: str
        values: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                helm_package_version: Optional[str] = ..., 
                options: Optional[HelmMappingRuleProfileOptions] = ..., 
                release_name: Optional[str] = ..., 
                release_namespace: Optional[str] = ..., 
                values: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.HelmMappingRuleProfileOptions(Model):
        install_options: HelmInstallOptions
        upgrade_options: HelmUpgradeOptions

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                install_options: Optional[HelmInstallOptions] = ..., 
                upgrade_options: Optional[HelmUpgradeOptions] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.HelmUpgradeOptions(Model):
        atomic: str
        timeout: str
        wait: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                atomic: Optional[str] = ..., 
                timeout: Optional[str] = ..., 
                wait: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.HttpMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        GET = "Get"
        PATCH = "Patch"
        POST = "Post"
        PUT = "Put"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.IdType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN = "Open"
        SECRET = "Secret"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ImageArtifactProfile(Model):
        image_name: str
        image_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                image_name: Optional[str] = ..., 
                image_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ImageMappingRuleProfile(Model):
        user_configuration: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                user_configuration: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ManagedResourceGroupConfiguration(Model):
        location: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
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


    class azure.mgmt.hybridnetwork.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.hybridnetwork.models.ManifestArtifactFormat(Model):
        artifact_name: str
        artifact_type: Union[str, ArtifactType]
        artifact_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_name: Optional[str] = ..., 
                artifact_type: Optional[Union[str, ArtifactType]] = ..., 
                artifact_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.MappingRuleProfile(Model):
        application_enablement: Union[str, ApplicationEnablement]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_enablement: Optional[Union[str, ApplicationEnablement]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NFVIType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ARC_KUBERNETES = "AzureArcKubernetes"
        AZURE_CORE = "AzureCore"
        AZURE_OPERATOR_NEXUS = "AzureOperatorNexus"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.NFVIs(Model):
        name: str
        nfvi_type: Union[str, NFVIType]

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


    class azure.mgmt.hybridnetwork.models.NSDArtifactProfile(Model):
        artifact_name: str
        artifact_store_reference: ReferencedResource
        artifact_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_name: Optional[str] = ..., 
                artifact_store_reference: Optional[ReferencedResource] = ..., 
                artifact_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkFunction(TrackedResource):
        etag: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NetworkFunctionPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[NetworkFunctionPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkFunctionApplication(Model):
        depends_on_profile: DependsOnProfile
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkFunctionConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN = "Open"
        SECRET = "Secret"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: NetworkFunctionDefinitionGroupPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NetworkFunctionDefinitionGroupPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionGroupListResult(Model):
        next_link: str
        value: list[NetworkFunctionDefinitionGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[NetworkFunctionDefinitionGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionGroupPropertiesFormat(Model):
        description: str
        provisioning_state: Union[str, ProvisioningState]

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


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionResourceElementTemplateDetails(ResourceElementTemplate):
        configuration: ArmResourceDefinitionResourceElementTemplate
        depends_on_profile: DependsOnProfile
        name: str
        resource_element_type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ArmResourceDefinitionResourceElementTemplate] = ..., 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionVersion(TrackedResource):
        id: str
        location: str
        name: str
        properties: NetworkFunctionDefinitionVersionPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NetworkFunctionDefinitionVersionPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionVersionListResult(Model):
        next_link: str
        value: list[NetworkFunctionDefinitionVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[NetworkFunctionDefinitionVersion]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionVersionPropertiesFormat(Model):
        deploy_parameters: str
        description: str
        network_function_type: Union[str, NetworkFunctionType]
        provisioning_state: Union[str, ProvisioningState]
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deploy_parameters: Optional[str] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkFunctionDefinitionVersionUpdateState(Model):
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                version_state: Optional[Union[str, VersionState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkFunctionListResult(Model):
        next_link: str
        value: list[NetworkFunction]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[NetworkFunction]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkFunctionPropertiesFormat(Model):
        allow_software_update: bool
        configuration_type: Union[str, NetworkFunctionConfigurationType]
        network_function_definition_group_name: str
        network_function_definition_offering_location: str
        network_function_definition_version: str
        network_function_definition_version_resource_reference: DeploymentResourceIdReference
        nfvi_id: str
        nfvi_type: Union[str, NFVIType]
        provisioning_state: Union[str, ProvisioningState]
        publisher_name: str
        publisher_scope: Union[str, PublisherScope]
        role_override_values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_software_update: Optional[bool] = ..., 
                network_function_definition_version_resource_reference: Optional[DeploymentResourceIdReference] = ..., 
                nfvi_id: Optional[str] = ..., 
                nfvi_type: Optional[Union[str, NFVIType]] = ..., 
                role_override_values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkFunctionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINERIZED_NETWORK_FUNCTION = "ContainerizedNetworkFunction"
        UNKNOWN = "Unknown"
        VIRTUAL_NETWORK_FUNCTION = "VirtualNetworkFunction"


    class azure.mgmt.hybridnetwork.models.NetworkFunctionValueWithSecrets(NetworkFunctionPropertiesFormat):
        allow_software_update: bool
        configuration_type: Union[str, NetworkFunctionConfigurationType]
        network_function_definition_group_name: str
        network_function_definition_offering_location: str
        network_function_definition_version: str
        network_function_definition_version_resource_reference: DeploymentResourceIdReference
        nfvi_id: str
        nfvi_type: Union[str, NFVIType]
        provisioning_state: Union[str, ProvisioningState]
        publisher_name: str
        publisher_scope: Union[str, PublisherScope]
        role_override_values: list[str]
        secret_deployment_values: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_software_update: Optional[bool] = ..., 
                network_function_definition_version_resource_reference: Optional[DeploymentResourceIdReference] = ..., 
                nfvi_id: Optional[str] = ..., 
                nfvi_type: Optional[Union[str, NFVIType]] = ..., 
                role_override_values: Optional[List[str]] = ..., 
                secret_deployment_values: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkFunctionValueWithoutSecrets(NetworkFunctionPropertiesFormat):
        allow_software_update: bool
        configuration_type: Union[str, NetworkFunctionConfigurationType]
        deployment_values: str
        network_function_definition_group_name: str
        network_function_definition_offering_location: str
        network_function_definition_version: str
        network_function_definition_version_resource_reference: DeploymentResourceIdReference
        nfvi_id: str
        nfvi_type: Union[str, NFVIType]
        provisioning_state: Union[str, ProvisioningState]
        publisher_name: str
        publisher_scope: Union[str, PublisherScope]
        role_override_values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_software_update: Optional[bool] = ..., 
                deployment_values: Optional[str] = ..., 
                network_function_definition_version_resource_reference: Optional[DeploymentResourceIdReference] = ..., 
                nfvi_id: Optional[str] = ..., 
                nfvi_type: Optional[Union[str, NFVIType]] = ..., 
                role_override_values: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkServiceDesignGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: NetworkServiceDesignGroupPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NetworkServiceDesignGroupPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkServiceDesignGroupListResult(Model):
        next_link: str
        value: list[NetworkServiceDesignGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[NetworkServiceDesignGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkServiceDesignGroupPropertiesFormat(Model):
        description: str
        provisioning_state: Union[str, ProvisioningState]

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


    class azure.mgmt.hybridnetwork.models.NetworkServiceDesignVersion(TrackedResource):
        id: str
        location: str
        name: str
        properties: NetworkServiceDesignVersionPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NetworkServiceDesignVersionPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.NetworkServiceDesignVersionListResult(Model):
        next_link: str
        value: list[NetworkServiceDesignVersion]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[NetworkServiceDesignVersion]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkServiceDesignVersionPropertiesFormat(Model):
        configuration_group_schema_references: dict[str, ReferencedResource]
        description: str
        nfvis_from_site: dict[str, NfviDetails]
        provisioning_state: Union[str, ProvisioningState]
        resource_element_templates: list[ResourceElementTemplate]
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration_group_schema_references: Optional[Dict[str, ReferencedResource]] = ..., 
                description: Optional[str] = ..., 
                nfvis_from_site: Optional[Dict[str, NfviDetails]] = ..., 
                resource_element_templates: Optional[List[ResourceElementTemplate]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NetworkServiceDesignVersionUpdateState(Model):
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                version_state: Optional[Union[str, VersionState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.NfviDetails(Model):
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


    class azure.mgmt.hybridnetwork.models.OpenDeploymentResourceReference(DeploymentResourceIdReference):
        id: str
        id_type: Union[str, IdType]

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


    class azure.mgmt.hybridnetwork.models.Operation(Model):
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


    class azure.mgmt.hybridnetwork.models.OperationDisplay(Model):
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


    class azure.mgmt.hybridnetwork.models.OperationListResult(Model):
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


    class azure.mgmt.hybridnetwork.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.hybridnetwork.models.Pod(Model):
        creation_time: datetime
        desired: int
        events: list[PodEvent]
        name: str
        namespace: str
        ready: int
        status: Union[str, PodStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                desired: Optional[int] = ..., 
                events: Optional[List[PodEvent]] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                ready: Optional[int] = ..., 
                status: Optional[Union[str, PodStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.PodEvent(Model):
        last_seen_time: datetime
        message: str
        reason: str
        type: Union[str, PodEventType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                last_seen_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                reason: Optional[str] = ..., 
                type: Optional[Union[str, PodEventType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.PodEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NORMAL = "Normal"
        WARNING = "Warning"


    class azure.mgmt.hybridnetwork.models.PodStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        NOT_READY = "NotReady"
        PENDING = "Pending"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TERMINATING = "Terminating"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CONVERGING = "Converging"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ProxyArtifactListOverview(ProxyResource):
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


    class azure.mgmt.hybridnetwork.models.ProxyArtifactOverview(ProxyResource):
        id: str
        name: str
        properties: ProxyArtifactOverviewPropertiesFormat
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


    class azure.mgmt.hybridnetwork.models.ProxyArtifactOverviewListResult(Model):
        next_link: str
        value: list[ProxyArtifactListOverview]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ProxyArtifactListOverview]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ProxyArtifactOverviewPropertiesFormat(Model):
        artifact_versions: list[ProxyArtifactOverviewPropertiesValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_versions: Optional[List[ProxyArtifactOverviewPropertiesValue]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ProxyArtifactOverviewPropertiesValue(Model):
        artifact_state: Union[str, ArtifactState]
        artifact_type: Union[str, ArtifactType]
        artifact_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                artifact_state: Optional[Union[str, ArtifactState]] = ..., 
                artifact_type: Optional[Union[str, ArtifactType]] = ..., 
                artifact_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ProxyArtifactVersionsListOverview(ProxyResource):
        id: str
        name: str
        properties: ProxyArtifactOverviewPropertiesValue
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


    class azure.mgmt.hybridnetwork.models.ProxyArtifactVersionsOverviewListResult(Model):
        next_link: str
        value: list[ProxyArtifactVersionsListOverview]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ProxyArtifactVersionsListOverview]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.ProxyResource(Resource):
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


    class azure.mgmt.hybridnetwork.models.Publisher(TrackedResource):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: PublisherPropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[PublisherPropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.PublisherListResult(Model):
        next_link: str
        value: list[Publisher]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Publisher]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.PublisherPropertiesFormat(Model):
        provisioning_state: Union[str, ProvisioningState]
        scope: Union[str, PublisherScope]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scope: Optional[Union[str, PublisherScope]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.PublisherScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.ReferencedResource(Model):
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


    class azure.mgmt.hybridnetwork.models.ReplicaSet(Model):
        creation_time: datetime
        current: int
        desired: int
        name: str
        namespace: str
        ready: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                current: Optional[int] = ..., 
                desired: Optional[int] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                ready: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.RequestMetadata(Model):
        api_version: str
        http_method: Union[str, HttpMethod]
        relative_path: str
        serialized_body: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                http_method: Union[str, HttpMethod], 
                relative_path: str, 
                serialized_body: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.Resource(Model):
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


    class azure.mgmt.hybridnetwork.models.ResourceElementTemplate(Model):
        depends_on_profile: DependsOnProfile
        name: str
        resource_element_type: Union[str, Type]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on_profile: Optional[DependsOnProfile] = ..., 
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


    class azure.mgmt.hybridnetwork.models.Resources(Model):
        daemon_sets: list[DaemonSet]
        deployments: list[Deployment]
        pods: list[Pod]
        replica_sets: list[ReplicaSet]
        stateful_sets: list[StatefulSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                daemon_sets: Optional[List[DaemonSet]] = ..., 
                deployments: Optional[List[Deployment]] = ..., 
                pods: Optional[List[Pod]] = ..., 
                replica_sets: Optional[List[ReplicaSet]] = ..., 
                stateful_sets: Optional[List[StatefulSet]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.SecretDeploymentResourceReference(DeploymentResourceIdReference):
        id: str
        id_type: Union[str, IdType]

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


    class azure.mgmt.hybridnetwork.models.Site(TrackedResource):
        id: str
        location: str
        name: str
        properties: SitePropertiesFormat
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SitePropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.SiteListResult(Model):
        next_link: str
        value: list[Site]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Site]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.SiteNetworkService(TrackedResource):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SiteNetworkServicePropertiesFormat
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[SiteNetworkServicePropertiesFormat] = ..., 
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


    class azure.mgmt.hybridnetwork.models.SiteNetworkServiceListResult(Model):
        next_link: str
        value: list[SiteNetworkService]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SiteNetworkService]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.SiteNetworkServicePropertiesFormat(Model):
        desired_state_configuration_group_value_references: dict[str, ReferencedResource]
        last_state_configuration_group_value_references: dict[str, ReferencedResource]
        last_state_network_service_design_version_name: str
        managed_resource_group_configuration: ManagedResourceGroupConfiguration
        network_service_design_group_name: str
        network_service_design_version_name: str
        network_service_design_version_offering_location: str
        network_service_design_version_resource_reference: DeploymentResourceIdReference
        provisioning_state: Union[str, ProvisioningState]
        publisher_name: str
        publisher_scope: Union[str, PublisherScope]
        site_reference: ReferencedResource

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                desired_state_configuration_group_value_references: Optional[Dict[str, ReferencedResource]] = ..., 
                managed_resource_group_configuration: Optional[ManagedResourceGroupConfiguration] = ..., 
                network_service_design_version_resource_reference: Optional[DeploymentResourceIdReference] = ..., 
                site_reference: Optional[ReferencedResource] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.SitePropertiesFormat(Model):
        nfvis: list[NFVIs]
        provisioning_state: Union[str, ProvisioningState]
        site_network_service_references: list[ReferencedResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                nfvis: Optional[List[NFVIs]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.Sku(Model):
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Union[str, SkuName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.hybridnetwork.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.hybridnetwork.models.StatefulSet(Model):
        creation_time: datetime
        desired: int
        name: str
        namespace: str
        ready: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creation_time: Optional[datetime] = ..., 
                desired: Optional[int] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                ready: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPLOYED = "Deployed"
        DOWNLOADING = "Downloading"
        FAILED = "Failed"
        INSTALLING = "Installing"
        PENDING_INSTALL = "Pending-Install"
        PENDING_ROLLBACK = "Pending-Rollback"
        PENDING_UPGRADE = "Pending-Upgrade"
        REINSTALLING = "Reinstalling"
        ROLLINGBACK = "Rollingback"
        SUPERSEDED = "Superseded"
        UNINSTALLED = "Uninstalled"
        UNINSTALLING = "Uninstalling"
        UNKNOWN = "Unknown"
        UPGRADING = "Upgrading"


    class azure.mgmt.hybridnetwork.models.SystemData(Model):
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


    class azure.mgmt.hybridnetwork.models.TagsObject(Model):
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


    class azure.mgmt.hybridnetwork.models.TemplateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM_TEMPLATE = "ArmTemplate"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.TrackedResource(Resource):
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


    class azure.mgmt.hybridnetwork.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM_RESOURCE_DEFINITION = "ArmResourceDefinition"
        NETWORK_FUNCTION_DEFINITION = "NetworkFunctionDefinition"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.UserAssignedIdentity(Model):
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


    class azure.mgmt.hybridnetwork.models.VersionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DEPRECATED = "Deprecated"
        PREVIEW = "Preview"
        UNKNOWN = "Unknown"
        VALIDATING = "Validating"
        VALIDATION_FAILED = "ValidationFailed"


    class azure.mgmt.hybridnetwork.models.VhdImageArtifactProfile(Model):
        vhd_name: str
        vhd_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                vhd_name: Optional[str] = ..., 
                vhd_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.VhdImageMappingRuleProfile(Model):
        user_configuration: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                user_configuration: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.VirtualNetworkFunctionDefinitionVersion(NetworkFunctionDefinitionVersionPropertiesFormat):
        deploy_parameters: str
        description: str
        network_function_template: VirtualNetworkFunctionTemplate
        network_function_type: Union[str, NetworkFunctionType]
        provisioning_state: Union[str, ProvisioningState]
        version_state: Union[str, VersionState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deploy_parameters: Optional[str] = ..., 
                description: Optional[str] = ..., 
                network_function_template: Optional[VirtualNetworkFunctionTemplate] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.hybridnetwork.models.VirtualNetworkFunctionNFVIType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CORE = "AzureCore"
        AZURE_OPERATOR_NEXUS = "AzureOperatorNexus"
        UNKNOWN = "Unknown"


    class azure.mgmt.hybridnetwork.models.VirtualNetworkFunctionTemplate(Model):
        nfvi_type: Union[str, VirtualNetworkFunctionNFVIType]

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


namespace azure.mgmt.hybridnetwork.operations

    class azure.mgmt.hybridnetwork.operations.ArtifactManifestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: ArtifactManifest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArtifactManifest]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArtifactManifest]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: ArtifactManifestUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArtifactManifestUpdateState]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArtifactManifestUpdateState]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactManifest: ...

        @distributed_trace
        def list_by_artifact_store(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ArtifactManifest]: ...

        @distributed_trace
        def list_credential(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactAccessCredential: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactManifest: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_manifest_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactManifest: ...


    class azure.mgmt.hybridnetwork.operations.ArtifactStoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: ArtifactStore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArtifactStore]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArtifactStore]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ArtifactStore: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ArtifactStore]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactStore: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArtifactStore: ...


    class azure.mgmt.hybridnetwork.operations.ComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                component_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Component: ...

        @distributed_trace
        def list_by_network_function(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Component]: ...


    class azure.mgmt.hybridnetwork.operations.ConfigurationGroupSchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: ConfigurationGroupSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationGroupSchema]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationGroupSchema]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: ConfigurationGroupSchemaVersionUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationGroupSchemaVersionUpdateState]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationGroupSchemaVersionUpdateState]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationGroupSchema: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationGroupSchema]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupSchema: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                configuration_group_schema_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupSchema: ...


    class azure.mgmt.hybridnetwork.operations.ConfigurationGroupValuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: ConfigurationGroupValue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationGroupValue]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ConfigurationGroupValue]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationGroupValue: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationGroupValue]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationGroupValue]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupValue: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                configuration_group_value_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationGroupValue: ...


    class azure.mgmt.hybridnetwork.operations.NetworkFunctionDefinitionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: NetworkFunctionDefinitionGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunctionDefinitionGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunctionDefinitionGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionGroup: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFunctionDefinitionGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionGroup: ...


    class azure.mgmt.hybridnetwork.operations.NetworkFunctionDefinitionVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: NetworkFunctionDefinitionVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunctionDefinitionVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunctionDefinitionVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: NetworkFunctionDefinitionVersionUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunctionDefinitionVersionUpdateState]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunctionDefinitionVersionUpdateState]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionVersion: ...

        @distributed_trace
        def list_by_network_function_definition_group(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFunctionDefinitionVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_function_definition_group_name: str, 
                network_function_definition_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunctionDefinitionVersion: ...


    class azure.mgmt.hybridnetwork.operations.NetworkFunctionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: NetworkFunction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunction]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkFunction]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute_request(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: ExecuteRequestParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute_request(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkFunction: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFunction]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkFunction]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunction: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                network_function_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkFunction: ...


    class azure.mgmt.hybridnetwork.operations.NetworkServiceDesignGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: NetworkServiceDesignGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkServiceDesignGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkServiceDesignGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkServiceDesignGroup: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkServiceDesignGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignGroup: ...


    class azure.mgmt.hybridnetwork.operations.NetworkServiceDesignVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: NetworkServiceDesignVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkServiceDesignVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkServiceDesignVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: NetworkServiceDesignVersionUpdateState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkServiceDesignVersionUpdateState]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkServiceDesignVersionUpdateState]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> NetworkServiceDesignVersion: ...

        @distributed_trace
        def list_by_network_service_design_group(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[NetworkServiceDesignVersion]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignVersion: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                network_service_design_group_name: str, 
                network_service_design_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkServiceDesignVersion: ...


    class azure.mgmt.hybridnetwork.operations.Operations:

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


    class azure.mgmt.hybridnetwork.operations.ProxyArtifactOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_name: str, 
                artifact_version_name: str, 
                parameters: ArtifactChangeState, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProxyArtifactVersionsListOverview]: ...

        @overload
        def begin_update_state(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_name: str, 
                artifact_version_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProxyArtifactVersionsListOverview]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                artifact_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ProxyArtifactVersionsListOverview]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                artifact_store_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ProxyArtifactListOverview]: ...


    class azure.mgmt.hybridnetwork.operations.PublishersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[Publisher] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Publisher]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Publisher]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Publisher: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Publisher]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Publisher]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[TagsObject] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Publisher: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                publisher_name: str, 
                parameters: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Publisher: ...


    class azure.mgmt.hybridnetwork.operations.SiteNetworkServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: SiteNetworkService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteNetworkService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SiteNetworkService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SiteNetworkService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SiteNetworkService]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SiteNetworkService]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteNetworkService: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                site_network_service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SiteNetworkService: ...


    class azure.mgmt.hybridnetwork.operations.SitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: Site, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Site]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                site_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                site_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Site: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Site]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Site]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                site_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Site: ...


```