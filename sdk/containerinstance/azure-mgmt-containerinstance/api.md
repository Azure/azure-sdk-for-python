```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.containerinstance

    class azure.mgmt.containerinstance.ContainerInstanceManagementClient: implements ContextManager 
        container_group_profile: ContainerGroupProfileOperations
        container_group_profiles: ContainerGroupProfilesOperations
        container_groups: ContainerGroupsOperations
        containers: ContainersOperations
        location: LocationOperations
        operations: Operations
        subnet_service_association_link: SubnetServiceAssociationLinkOperations

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


namespace azure.mgmt.containerinstance.aio

    class azure.mgmt.containerinstance.aio.ContainerInstanceManagementClient: implements AsyncContextManager 
        container_group_profile: ContainerGroupProfileOperations
        container_group_profiles: ContainerGroupProfilesOperations
        container_groups: ContainerGroupsOperations
        containers: ContainersOperations
        location: LocationOperations
        operations: Operations
        subnet_service_association_link: SubnetServiceAssociationLinkOperations

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


namespace azure.mgmt.containerinstance.aio.operations

    class azure.mgmt.containerinstance.aio.operations.ContainerGroupProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_revision_number(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                revision_number: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def list_all_revisions(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ContainerGroupProfile]: ...


    class azure.mgmt.containerinstance.aio.operations.ContainerGroupProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: ContainerGroupProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[ContainerGroupProfile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ContainerGroupProfile]: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: ContainerGroupProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...


    class azure.mgmt.containerinstance.aio.operations.ContainerGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: ContainerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ContainerGroup]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @distributed_trace_async
        async def get_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> List[str]: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[ContainerGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ContainerGroup]: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: Resource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...


    class azure.mgmt.containerinstance.aio.operations.ContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def attach(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ContainerAttachResponse: ...

        @overload
        async def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: ContainerExecRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @overload
        async def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @distributed_trace_async
        async def list_logs(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                tail: Optional[int] = None, 
                timestamps: Optional[bool] = None, 
                **kwargs: Any
            ) -> Logs: ...


    class azure.mgmt.containerinstance.aio.operations.LocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_cached_images(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncIterable[CachedImages]: ...

        @distributed_trace
        def list_capabilities(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncIterable[Capabilities]: ...

        @distributed_trace
        def list_usage(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


    class azure.mgmt.containerinstance.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.containerinstance.aio.operations.SubnetServiceAssociationLinkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


namespace azure.mgmt.containerinstance.models

    class azure.mgmt.containerinstance.models.AzureFileVolume(Model):
        read_only: bool
        share_name: str
        storage_account_key: str
        storage_account_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                read_only: Optional[bool] = ..., 
                share_name: str, 
                storage_account_key: Optional[str] = ..., 
                storage_account_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.CachedImages(Model):
        image: str
        os_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                image: str, 
                os_type: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.CachedImagesListResult(Model):
        next_link: str
        value: list[CachedImages]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[CachedImages]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.Capabilities(Model):
        capabilities: CapabilitiesCapabilities
        gpu: str
        ip_address_type: str
        location: str
        os_type: str
        resource_type: str

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


    class azure.mgmt.containerinstance.models.CapabilitiesCapabilities(Model):
        max_cpu: float
        max_gpu_count: float
        max_memory_in_gb: float

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


    class azure.mgmt.containerinstance.models.CapabilitiesListResult(Model):
        next_link: str
        value: list[Capabilities]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Capabilities]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.CloudErrorBody(Model):
        code: str
        details: list[CloudErrorBody]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ConfidentialComputeProperties(Model):
        cce_policy: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cce_policy: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ConfigMap(Model):
        key_value_pairs: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_value_pairs: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.Container(Model):
        command: list[str]
        config_map: ConfigMap
        environment_variables: list[EnvironmentVariable]
        image: str
        instance_view: ContainerPropertiesInstanceView
        liveness_probe: ContainerProbe
        name: str
        ports: list[ContainerPort]
        readiness_probe: ContainerProbe
        resources: ResourceRequirements
        security_context: SecurityContextDefinition
        volume_mounts: list[VolumeMount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                command: Optional[List[str]] = ..., 
                config_map: Optional[ConfigMap] = ..., 
                environment_variables: Optional[List[EnvironmentVariable]] = ..., 
                image: Optional[str] = ..., 
                liveness_probe: Optional[ContainerProbe] = ..., 
                name: str, 
                ports: Optional[List[ContainerPort]] = ..., 
                readiness_probe: Optional[ContainerProbe] = ..., 
                resources: Optional[ResourceRequirements] = ..., 
                security_context: Optional[SecurityContextDefinition] = ..., 
                volume_mounts: Optional[List[VolumeMount]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerAttachResponse(Model):
        password: str
        web_socket_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                web_socket_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerExec(Model):
        command: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                command: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerExecRequest(Model):
        command: str
        terminal_size: ContainerExecRequestTerminalSize

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                command: Optional[str] = ..., 
                terminal_size: Optional[ContainerExecRequestTerminalSize] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerExecRequestTerminalSize(Model):
        cols: int
        rows: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cols: Optional[int] = ..., 
                rows: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerExecResponse(Model):
        password: str
        web_socket_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                web_socket_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroup(Resource, ContainerGroupProperties):
        confidential_compute_properties: ConfidentialComputeProperties
        container_group_profile: ContainerGroupProfileReferenceDefinition
        containers: list[Container]
        diagnostics: ContainerGroupDiagnostics
        dns_config: DnsConfiguration
        encryption_properties: EncryptionProperties
        extensions: list[DeploymentExtensionSpec]
        id: str
        identity: ContainerGroupIdentity
        image_registry_credentials: list[ImageRegistryCredential]
        init_containers: list[InitContainerDefinition]
        instance_view: ContainerGroupPropertiesInstanceView
        ip_address: IpAddress
        is_created_from_standby_pool: bool
        location: str
        name: str
        os_type: Union[str, OperatingSystemTypes]
        priority: Union[str, ContainerGroupPriority]
        provisioning_state: str
        restart_policy: Union[str, ContainerGroupRestartPolicy]
        sku: Union[str, ContainerGroupSku]
        standby_pool_profile: StandbyPoolProfileDefinition
        subnet_ids: list[ContainerGroupSubnetId]
        tags: dict[str, str]
        type: str
        volumes: list[Volume]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                confidential_compute_properties: Optional[ConfidentialComputeProperties] = ..., 
                container_group_profile: Optional[ContainerGroupProfileReferenceDefinition] = ..., 
                containers: List[Container], 
                diagnostics: Optional[ContainerGroupDiagnostics] = ..., 
                dns_config: Optional[DnsConfiguration] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                extensions: Optional[List[DeploymentExtensionSpec]] = ..., 
                identity: Optional[ContainerGroupIdentity] = ..., 
                image_registry_credentials: Optional[List[ImageRegistryCredential]] = ..., 
                init_containers: Optional[List[InitContainerDefinition]] = ..., 
                ip_address: Optional[IpAddress] = ..., 
                location: Optional[str] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                priority: Optional[Union[str, ContainerGroupPriority]] = ..., 
                restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]] = ..., 
                sku: Optional[Union[str, ContainerGroupSku]] = ..., 
                standby_pool_profile: Optional[StandbyPoolProfileDefinition] = ..., 
                subnet_ids: Optional[List[ContainerGroupSubnetId]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                volumes: Optional[List[Volume]] = ..., 
                zones: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupDiagnostics(Model):
        log_analytics: LogAnalytics

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_analytics: Optional[LogAnalytics] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentities]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentities]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupIpAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.containerinstance.models.ContainerGroupListResult(Model):
        next_link: str
        value: list[ContainerGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ContainerGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupNetworkProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.containerinstance.models.ContainerGroupPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.containerinstance.models.ContainerGroupProfile(Resource, ContainerGroupProfileProperties):
        confidential_compute_properties: ConfidentialComputeProperties
        containers: list[Container]
        diagnostics: ContainerGroupDiagnostics
        encryption_properties: EncryptionProperties
        extensions: list[DeploymentExtensionSpec]
        id: str
        image_registry_credentials: list[ImageRegistryCredential]
        init_containers: list[InitContainerDefinition]
        ip_address: IpAddress
        location: str
        name: str
        os_type: Union[str, OperatingSystemTypes]
        priority: Union[str, ContainerGroupPriority]
        restart_policy: Union[str, ContainerGroupRestartPolicy]
        revision: int
        sku: Union[str, ContainerGroupSku]
        tags: dict[str, str]
        type: str
        volumes: list[Volume]
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                confidential_compute_properties: Optional[ConfidentialComputeProperties] = ..., 
                containers: List[Container], 
                diagnostics: Optional[ContainerGroupDiagnostics] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                extensions: Optional[List[DeploymentExtensionSpec]] = ..., 
                image_registry_credentials: Optional[List[ImageRegistryCredential]] = ..., 
                init_containers: Optional[List[InitContainerDefinition]] = ..., 
                ip_address: Optional[IpAddress] = ..., 
                location: Optional[str] = ..., 
                os_type: Union[str, OperatingSystemTypes], 
                priority: Optional[Union[str, ContainerGroupPriority]] = ..., 
                restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]] = ..., 
                sku: Optional[Union[str, ContainerGroupSku]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                volumes: Optional[List[Volume]] = ..., 
                zones: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProfileListResult(Model):
        next_link: str
        value: list[ContainerGroupProfile]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ContainerGroupProfile]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProfilePatch(Model):
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


    class azure.mgmt.containerinstance.models.ContainerGroupProfileProperties(Model):
        confidential_compute_properties: ConfidentialComputeProperties
        containers: list[Container]
        diagnostics: ContainerGroupDiagnostics
        encryption_properties: EncryptionProperties
        extensions: list[DeploymentExtensionSpec]
        image_registry_credentials: list[ImageRegistryCredential]
        init_containers: list[InitContainerDefinition]
        ip_address: IpAddress
        os_type: Union[str, OperatingSystemTypes]
        priority: Union[str, ContainerGroupPriority]
        restart_policy: Union[str, ContainerGroupRestartPolicy]
        revision: int
        sku: Union[str, ContainerGroupSku]
        volumes: list[Volume]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                confidential_compute_properties: Optional[ConfidentialComputeProperties] = ..., 
                containers: List[Container], 
                diagnostics: Optional[ContainerGroupDiagnostics] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                extensions: Optional[List[DeploymentExtensionSpec]] = ..., 
                image_registry_credentials: Optional[List[ImageRegistryCredential]] = ..., 
                init_containers: Optional[List[InitContainerDefinition]] = ..., 
                ip_address: Optional[IpAddress] = ..., 
                os_type: Union[str, OperatingSystemTypes], 
                priority: Optional[Union[str, ContainerGroupPriority]] = ..., 
                restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]] = ..., 
                sku: Optional[Union[str, ContainerGroupSku]] = ..., 
                volumes: Optional[List[Volume]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProfileReferenceDefinition(Model):
        id: str
        revision: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                revision: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupProperties(Model):
        confidential_compute_properties: ConfidentialComputeProperties
        container_group_profile: ContainerGroupProfileReferenceDefinition
        containers: list[Container]
        diagnostics: ContainerGroupDiagnostics
        dns_config: DnsConfiguration
        encryption_properties: EncryptionProperties
        extensions: list[DeploymentExtensionSpec]
        identity: ContainerGroupIdentity
        image_registry_credentials: list[ImageRegistryCredential]
        init_containers: list[InitContainerDefinition]
        instance_view: ContainerGroupPropertiesInstanceView
        ip_address: IpAddress
        is_created_from_standby_pool: bool
        os_type: Union[str, OperatingSystemTypes]
        priority: Union[str, ContainerGroupPriority]
        provisioning_state: str
        restart_policy: Union[str, ContainerGroupRestartPolicy]
        sku: Union[str, ContainerGroupSku]
        standby_pool_profile: StandbyPoolProfileDefinition
        subnet_ids: list[ContainerGroupSubnetId]
        volumes: list[Volume]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                confidential_compute_properties: Optional[ConfidentialComputeProperties] = ..., 
                container_group_profile: Optional[ContainerGroupProfileReferenceDefinition] = ..., 
                containers: List[Container], 
                diagnostics: Optional[ContainerGroupDiagnostics] = ..., 
                dns_config: Optional[DnsConfiguration] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                extensions: Optional[List[DeploymentExtensionSpec]] = ..., 
                identity: Optional[ContainerGroupIdentity] = ..., 
                image_registry_credentials: Optional[List[ImageRegistryCredential]] = ..., 
                init_containers: Optional[List[InitContainerDefinition]] = ..., 
                ip_address: Optional[IpAddress] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                priority: Optional[Union[str, ContainerGroupPriority]] = ..., 
                restart_policy: Optional[Union[str, ContainerGroupRestartPolicy]] = ..., 
                sku: Optional[Union[str, ContainerGroupSku]] = ..., 
                standby_pool_profile: Optional[StandbyPoolProfileDefinition] = ..., 
                subnet_ids: Optional[List[ContainerGroupSubnetId]] = ..., 
                volumes: Optional[List[Volume]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerGroupPropertiesInstanceView(Model):
        events: list[Event]
        state: str

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


    class azure.mgmt.containerinstance.models.ContainerGroupRestartPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        NEVER = "Never"
        ON_FAILURE = "OnFailure"


    class azure.mgmt.containerinstance.models.ContainerGroupSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL = "Confidential"
        DEDICATED = "Dedicated"
        STANDARD = "Standard"


    class azure.mgmt.containerinstance.models.ContainerGroupSubnetId(Model):
        id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
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


    class azure.mgmt.containerinstance.models.ContainerHttpGet(Model):
        http_headers: list[HttpHeader]
        path: str
        port: int
        scheme: Union[str, Scheme]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                http_headers: Optional[List[HttpHeader]] = ..., 
                path: Optional[str] = ..., 
                port: int, 
                scheme: Optional[Union[str, Scheme]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerInstanceOperationsOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.containerinstance.models.ContainerNetworkProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.containerinstance.models.ContainerPort(Model):
        port: int
        protocol: Union[str, ContainerNetworkProtocol]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                port: int, 
                protocol: Optional[Union[str, ContainerNetworkProtocol]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerProbe(Model):
        exec_property: ContainerExec
        failure_threshold: int
        http_get: ContainerHttpGet
        initial_delay_seconds: int
        period_seconds: int
        success_threshold: int
        timeout_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                exec_property: Optional[ContainerExec] = ..., 
                failure_threshold: Optional[int] = ..., 
                http_get: Optional[ContainerHttpGet] = ..., 
                initial_delay_seconds: Optional[int] = ..., 
                period_seconds: Optional[int] = ..., 
                success_threshold: Optional[int] = ..., 
                timeout_seconds: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ContainerPropertiesInstanceView(Model):
        current_state: ContainerState
        events: list[Event]
        previous_state: ContainerState
        restart_count: int

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


    class azure.mgmt.containerinstance.models.ContainerState(Model):
        detail_status: str
        exit_code: int
        finish_time: datetime
        start_time: datetime
        state: str

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


    class azure.mgmt.containerinstance.models.DeploymentExtensionSpec(Model):
        extension_type: str
        name: str
        protected_settings: JSON
        settings: JSON
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extension_type: Optional[str] = ..., 
                name: str, 
                protected_settings: Optional[JSON] = ..., 
                settings: Optional[JSON] = ..., 
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


    class azure.mgmt.containerinstance.models.DnsConfiguration(Model):
        name_servers: list[str]
        options: str
        search_domains: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name_servers: List[str], 
                options: Optional[str] = ..., 
                search_domains: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.DnsNameLabelReusePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOREUSE = "Noreuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"
        UNSECURE = "Unsecure"


    class azure.mgmt.containerinstance.models.EncryptionProperties(Model):
        identity: str
        key_name: str
        key_version: str
        vault_base_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                key_name: str, 
                key_version: str, 
                vault_base_url: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.EnvironmentVariable(Model):
        name: str
        secure_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                secure_value: Optional[str] = ..., 
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


    class azure.mgmt.containerinstance.models.Event(Model):
        count: int
        first_timestamp: datetime
        last_timestamp: datetime
        message: str
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


    class azure.mgmt.containerinstance.models.GitRepoVolume(Model):
        directory: str
        repository: str
        revision: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                directory: Optional[str] = ..., 
                repository: str, 
                revision: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.GpuResource(Model):
        count: int
        sku: Union[str, GpuSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: int, 
                sku: Union[str, GpuSku], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.GpuSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        K80 = "K80"
        P100 = "P100"
        V100 = "V100"


    class azure.mgmt.containerinstance.models.HttpHeader(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.containerinstance.models.ImageRegistryCredential(Model):
        identity: str
        identity_url: str
        password: str
        server: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                identity_url: Optional[str] = ..., 
                password: Optional[str] = ..., 
                server: str, 
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


    class azure.mgmt.containerinstance.models.InitContainerDefinition(Model):
        command: list[str]
        environment_variables: list[EnvironmentVariable]
        image: str
        instance_view: InitContainerPropertiesDefinitionInstanceView
        name: str
        security_context: SecurityContextDefinition
        volume_mounts: list[VolumeMount]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                command: Optional[List[str]] = ..., 
                environment_variables: Optional[List[EnvironmentVariable]] = ..., 
                image: Optional[str] = ..., 
                name: str, 
                security_context: Optional[SecurityContextDefinition] = ..., 
                volume_mounts: Optional[List[VolumeMount]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.InitContainerPropertiesDefinitionInstanceView(Model):
        current_state: ContainerState
        events: list[Event]
        previous_state: ContainerState
        restart_count: int

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


    class azure.mgmt.containerinstance.models.IpAddress(Model):
        auto_generated_domain_name_label_scope: Union[str, DnsNameLabelReusePolicy]
        dns_name_label: str
        fqdn: str
        ip: str
        ports: list[Port]
        type: Union[str, ContainerGroupIpAddressType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Union[str, DnsNameLabelReusePolicy] = "Unsecure", 
                dns_name_label: Optional[str] = ..., 
                ip: Optional[str] = ..., 
                ports: List[Port], 
                type: Union[str, ContainerGroupIpAddressType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.LogAnalytics(Model):
        log_type: Union[str, LogAnalyticsLogType]
        metadata: dict[str, str]
        workspace_id: str
        workspace_key: str
        workspace_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_type: Optional[Union[str, LogAnalyticsLogType]] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                workspace_id: str, 
                workspace_key: str, 
                workspace_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.LogAnalyticsLogType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_INSIGHTS = "ContainerInsights"
        CONTAINER_INSTANCE_LOGS = "ContainerInstanceLogs"


    class azure.mgmt.containerinstance.models.Logs(Model):
        content: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.containerinstance.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: Union[str, ContainerInstanceOperationsOrigin]
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: OperationDisplay, 
                name: str, 
                origin: Optional[Union[str, ContainerInstanceOperationsOrigin]] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.OperationDisplay(Model):
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


    class azure.mgmt.containerinstance.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.containerinstance.models.Port(Model):
        port: int
        protocol: Union[str, ContainerGroupNetworkProtocol]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                port: int, 
                protocol: Optional[Union[str, ContainerGroupNetworkProtocol]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.Resource(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str
        zones: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                zones: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerinstance.models.ResourceLimits(Model):
        cpu: float
        gpu: GpuResource
        memory_in_gb: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cpu: Optional[float] = ..., 
                gpu: Optional[GpuResource] = ..., 
                memory_in_gb: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ResourceRequests(Model):
        cpu: float
        gpu: GpuResource
        memory_in_gb: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cpu: float, 
                gpu: Optional[GpuResource] = ..., 
                memory_in_gb: float, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.ResourceRequirements(Model):
        limits: ResourceLimits
        requests: ResourceRequests

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                limits: Optional[ResourceLimits] = ..., 
                requests: ResourceRequests, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.Scheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        HTTPS = "https"


    class azure.mgmt.containerinstance.models.SecurityContextCapabilitiesDefinition(Model):
        add: list[str]
        drop: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                add: Optional[List[str]] = ..., 
                drop: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.SecurityContextDefinition(Model):
        allow_privilege_escalation: bool
        capabilities: SecurityContextCapabilitiesDefinition
        privileged: bool
        run_as_group: int
        run_as_user: int
        seccomp_profile: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_privilege_escalation: Optional[bool] = ..., 
                capabilities: Optional[SecurityContextCapabilitiesDefinition] = ..., 
                privileged: Optional[bool] = ..., 
                run_as_group: Optional[int] = ..., 
                run_as_user: Optional[int] = ..., 
                seccomp_profile: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.StandbyPoolProfileDefinition(Model):
        fail_container_group_create_on_reuse_failure: bool
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fail_container_group_create_on_reuse_failure: Optional[bool] = ..., 
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


    class azure.mgmt.containerinstance.models.Usage(Model):
        current_value: int
        id: str
        limit: int
        name: UsageName
        unit: str

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


    class azure.mgmt.containerinstance.models.UsageListResult(Model):
        value: list[Usage]

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


    class azure.mgmt.containerinstance.models.UsageName(Model):
        localized_value: str
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


    class azure.mgmt.containerinstance.models.UserAssignedIdentities(Model):
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


    class azure.mgmt.containerinstance.models.Volume(Model):
        azure_file: AzureFileVolume
        empty_dir: JSON
        git_repo: GitRepoVolume
        name: str
        secret: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_file: Optional[AzureFileVolume] = ..., 
                empty_dir: Optional[JSON] = ..., 
                git_repo: Optional[GitRepoVolume] = ..., 
                name: str, 
                secret: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.containerinstance.models.VolumeMount(Model):
        mount_path: str
        name: str
        read_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                mount_path: str, 
                name: str, 
                read_only: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.containerinstance.operations

    class azure.mgmt.containerinstance.operations.ContainerGroupProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_by_revision_number(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                revision_number: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def list_all_revisions(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> Iterable[ContainerGroupProfile]: ...


    class azure.mgmt.containerinstance.operations.ContainerGroupProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: ContainerGroupProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                container_group_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[ContainerGroupProfile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[ContainerGroupProfile]: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: ContainerGroupProfilePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                container_group_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroupProfile: ...


    class azure.mgmt.containerinstance.operations.ContainerGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: ContainerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContainerGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[ContainerGroup]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @distributed_trace
        def get_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> List[str]: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[ContainerGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[ContainerGroup]: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: Resource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerGroup: ...


    class azure.mgmt.containerinstance.operations.ContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def attach(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                **kwargs: Any
            ) -> ContainerAttachResponse: ...

        @overload
        def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: ContainerExecRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @overload
        def execute_command(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                container_exec_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ContainerExecResponse: ...

        @distributed_trace
        def list_logs(
                self, 
                resource_group_name: str, 
                container_group_name: str, 
                container_name: str, 
                tail: Optional[int] = None, 
                timestamps: Optional[bool] = None, 
                **kwargs: Any
            ) -> Logs: ...


    class azure.mgmt.containerinstance.operations.LocationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_cached_images(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[CachedImages]: ...

        @distributed_trace
        def list_capabilities(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[Capabilities]: ...

        @distributed_trace
        def list_usage(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


    class azure.mgmt.containerinstance.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.containerinstance.operations.SubnetServiceAssociationLinkOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                virtual_network_name: str, 
                subnet_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


```