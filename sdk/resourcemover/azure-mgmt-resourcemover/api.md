```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resourcemover

    class azure.mgmt.resourcemover.ResourceMoverServiceAPI: implements ContextManager 
        move_collections: MoveCollectionsOperations
        move_resources: MoveResourcesOperations
        operations_discovery: OperationsDiscoveryOperations
        unresolved_dependencies: UnresolvedDependenciesOperations

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


namespace azure.mgmt.resourcemover.aio

    class azure.mgmt.resourcemover.aio.ResourceMoverServiceAPI: implements AsyncContextManager 
        move_collections: MoveCollectionsOperations
        move_resources: MoveResourcesOperations
        operations_discovery: OperationsDiscoveryOperations
        unresolved_dependencies: UnresolvedDependenciesOperations

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


namespace azure.mgmt.resourcemover.aio.operations

    class azure.mgmt.resourcemover.aio.operations.MoveCollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_bulk_remove(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[BulkRemoveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_bulk_remove(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_commit(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[CommitRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_commit(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_discard(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[DiscardRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_discard(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_initiate_move(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[ResourceMoveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_initiate_move(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_prepare(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[PrepareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_prepare(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def begin_resolve_dependencies(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[MoveCollection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MoveCollection: ...

        @distributed_trace
        def list_move_collections_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[MoveCollection]: ...

        @distributed_trace
        def list_move_collections_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[MoveCollection]: ...

        @distributed_trace_async
        async def list_required_for(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                source_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RequiredForResourcesCollection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[UpdateMoveCollectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...


    class azure.mgmt.resourcemover.aio.operations.MoveResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                body: Optional[MoveResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MoveResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MoveResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MoveResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[MoveResource]: ...


    class azure.mgmt.resourcemover.aio.operations.OperationsDiscoveryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationsDiscoveryCollection: ...


    class azure.mgmt.resourcemover.aio.operations.UnresolvedDependenciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                dependency_level: Optional[Union[str, DependencyLevel]] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[UnresolvedDependency]: ...


namespace azure.mgmt.resourcemover.models

    class azure.mgmt.resourcemover.models.AffectedMoveResource(Model):
        id: str
        move_resources: list[AffectedMoveResource]
        source_id: str

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


    class azure.mgmt.resourcemover.models.AutomaticResolutionProperties(Model):
        move_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                move_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.AvailabilitySetResourceSettings(ResourceSettings):
        fault_domain: int
        resource_type: str
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str
        update_domain: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fault_domain: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                update_domain: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.AzureResourceReference(Model):
        source_arm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_arm_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.BulkRemoveRequest(Model):
        move_resource_input_type: Union[str, MoveResourceInputType]
        move_resources: list[str]
        validate_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                move_resource_input_type: Optional[Union[str, MoveResourceInputType]] = ..., 
                move_resources: Optional[List[str]] = ..., 
                validate_only: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.CloudErrorBody(Model):
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


    class azure.mgmt.resourcemover.models.CommitRequest(Model):
        move_resource_input_type: Union[str, MoveResourceInputType]
        move_resources: list[str]
        validate_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                move_resource_input_type: Optional[Union[str, MoveResourceInputType]] = ..., 
                move_resources: List[str], 
                validate_only: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resourcemover.models.DependencyLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESCENDANT = "Descendant"
        DIRECT = "Direct"


    class azure.mgmt.resourcemover.models.DependencyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUIRED_FOR_MOVE = "RequiredForMove"
        REQUIRED_FOR_PREPARE = "RequiredForPrepare"


    class azure.mgmt.resourcemover.models.DiscardRequest(Model):
        move_resource_input_type: Union[str, MoveResourceInputType]
        move_resources: list[str]
        validate_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                move_resource_input_type: Optional[Union[str, MoveResourceInputType]] = ..., 
                move_resources: List[str], 
                validate_only: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.DiskEncryptionSetResourceSettings(ResourceSettings):
        resource_type: str
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.Display(Model):
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


    class azure.mgmt.resourcemover.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.JobName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INITIAL_SYNC = "InitialSync"


    class azure.mgmt.resourcemover.models.JobStatus(Model):
        job_name: Union[str, JobName]
        job_progress: str

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


    class azure.mgmt.resourcemover.models.KeyVaultResourceSettings(ResourceSettings):
        resource_type: str
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.LBBackendAddressPoolResourceSettings(Model):
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


    class azure.mgmt.resourcemover.models.LBFrontendIPConfigurationResourceSettings(Model):
        name: str
        private_ip_address: str
        private_ip_allocation_method: str
        subnet: SubnetReference
        zones: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                private_ip_address: Optional[str] = ..., 
                private_ip_allocation_method: Optional[str] = ..., 
                subnet: Optional[SubnetReference] = ..., 
                zones: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.LoadBalancerBackendAddressPoolReference(ProxyResourceReference):
        name: str
        source_arm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                source_arm_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.LoadBalancerNatRuleReference(ProxyResourceReference):
        name: str
        source_arm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                source_arm_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.LoadBalancerResourceSettings(ResourceSettings):
        backend_address_pools: list[LBBackendAddressPoolResourceSettings]
        frontend_ip_configurations: list[LBFrontendIPConfigurationResourceSettings]
        resource_type: str
        sku: str
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str
        zones: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backend_address_pools: Optional[List[LBBackendAddressPoolResourceSettings]] = ..., 
                frontend_ip_configurations: Optional[List[LBFrontendIPConfigurationResourceSettings]] = ..., 
                sku: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                zones: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.ManualResolutionProperties(Model):
        target_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveCollection(Model):
        etag: str
        id: str
        identity: Identity
        location: str
        name: str
        properties: MoveCollectionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[MoveCollectionProperties] = ..., 
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


    class azure.mgmt.resourcemover.models.MoveCollectionProperties(Model):
        errors: MoveCollectionPropertiesErrors
        move_region: str
        move_type: Union[str, MoveType]
        provisioning_state: Union[str, ProvisioningState]
        source_region: str
        target_region: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                move_region: Optional[str] = ..., 
                move_type: Optional[Union[str, MoveType]] = ..., 
                source_region: Optional[str] = ..., 
                target_region: Optional[str] = ..., 
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


    class azure.mgmt.resourcemover.models.MoveCollectionPropertiesErrors(MoveResourceError):
        properties: MoveResourceErrorBody

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MoveResourceErrorBody] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveCollectionResultList(Model):
        next_link: str
        value: list[MoveCollection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[MoveCollection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveErrorInfo(Model):
        move_resources: list[AffectedMoveResource]

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


    class azure.mgmt.resourcemover.models.MoveResource(Model):
        id: str
        name: str
        properties: MoveResourceProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MoveResourceProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceCollection(Model):
        next_link: str
        summary_collection: SummaryCollection
        total_count: int
        value: list[MoveResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                summary_collection: Optional[SummaryCollection] = ..., 
                value: Optional[List[MoveResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceDependency(Model):
        automatic_resolution: AutomaticResolutionProperties
        dependency_type: Union[str, DependencyType]
        id: str
        is_optional: str
        manual_resolution: ManualResolutionProperties
        resolution_status: str
        resolution_type: Union[str, ResolutionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                automatic_resolution: Optional[AutomaticResolutionProperties] = ..., 
                dependency_type: Optional[Union[str, DependencyType]] = ..., 
                id: Optional[str] = ..., 
                is_optional: Optional[str] = ..., 
                manual_resolution: Optional[ManualResolutionProperties] = ..., 
                resolution_status: Optional[str] = ..., 
                resolution_type: Optional[Union[str, ResolutionType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceDependencyOverride(Model):
        id: str
        target_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                target_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceError(Model):
        properties: MoveResourceErrorBody

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MoveResourceErrorBody] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceErrorBody(Model):
        code: str
        details: list[MoveResourceErrorBody]
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


    class azure.mgmt.resourcemover.models.MoveResourceFilter(Model):
        properties: MoveResourceFilterProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MoveResourceFilterProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceFilterProperties(Model):
        provisioning_state: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                provisioning_state: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MOVE_RESOURCE_ID = "MoveResourceId"
        MOVE_RESOURCE_SOURCE_ID = "MoveResourceSourceId"


    class azure.mgmt.resourcemover.models.MoveResourceProperties(Model):
        depends_on: list[MoveResourceDependency]
        depends_on_overrides: list[MoveResourceDependencyOverride]
        errors: MoveResourcePropertiesErrors
        existing_target_id: str
        is_resolve_required: bool
        move_status: MoveResourcePropertiesMoveStatus
        provisioning_state: Union[str, ProvisioningState]
        resource_settings: ResourceSettings
        source_id: str
        source_resource_settings: ResourceSettings
        target_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                depends_on_overrides: Optional[List[MoveResourceDependencyOverride]] = ..., 
                existing_target_id: Optional[str] = ..., 
                resource_settings: Optional[ResourceSettings] = ..., 
                source_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourcePropertiesErrors(MoveResourceError):
        properties: MoveResourceErrorBody

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[MoveResourceErrorBody] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourcePropertiesMoveStatus(MoveResourceStatus):
        errors: MoveResourceError
        job_status: JobStatus
        move_state: Union[str, MoveState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                errors: Optional[MoveResourceError] = ..., 
                job_status: Optional[JobStatus] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveResourceStatus(Model):
        errors: MoveResourceError
        job_status: JobStatus
        move_state: Union[str, MoveState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                errors: Optional[MoveResourceError] = ..., 
                job_status: Optional[JobStatus] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.MoveState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGNMENT_PENDING = "AssignmentPending"
        COMMITTED = "Committed"
        COMMIT_FAILED = "CommitFailed"
        COMMIT_IN_PROGRESS = "CommitInProgress"
        COMMIT_PENDING = "CommitPending"
        DELETE_SOURCE_PENDING = "DeleteSourcePending"
        DISCARD_FAILED = "DiscardFailed"
        DISCARD_IN_PROGRESS = "DiscardInProgress"
        MOVE_FAILED = "MoveFailed"
        MOVE_IN_PROGRESS = "MoveInProgress"
        MOVE_PENDING = "MovePending"
        PREPARE_FAILED = "PrepareFailed"
        PREPARE_IN_PROGRESS = "PrepareInProgress"
        PREPARE_PENDING = "PreparePending"
        RESOURCE_MOVE_COMPLETED = "ResourceMoveCompleted"


    class azure.mgmt.resourcemover.models.MoveType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGION_TO_REGION = "RegionToRegion"
        REGION_TO_ZONE = "RegionToZone"


    class azure.mgmt.resourcemover.models.NetworkInterfaceResourceSettings(ResourceSettings):
        enable_accelerated_networking: bool
        ip_configurations: list[NicIpConfigurationResourceSettings]
        resource_type: str
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_accelerated_networking: Optional[bool] = ..., 
                ip_configurations: Optional[List[NicIpConfigurationResourceSettings]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.NetworkSecurityGroupResourceSettings(ResourceSettings):
        resource_type: str
        security_rules: list[NsgSecurityRule]
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                security_rules: Optional[List[NsgSecurityRule]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.NicIpConfigurationResourceSettings(Model):
        load_balancer_backend_address_pools: list[LoadBalancerBackendAddressPoolReference]
        load_balancer_nat_rules: list[LoadBalancerNatRuleReference]
        name: str
        primary: bool
        private_ip_address: str
        private_ip_allocation_method: str
        public_ip: PublicIpReference
        subnet: SubnetReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                load_balancer_backend_address_pools: Optional[List[LoadBalancerBackendAddressPoolReference]] = ..., 
                load_balancer_nat_rules: Optional[List[LoadBalancerNatRuleReference]] = ..., 
                name: Optional[str] = ..., 
                primary: Optional[bool] = ..., 
                private_ip_address: Optional[str] = ..., 
                private_ip_allocation_method: Optional[str] = ..., 
                public_ip: Optional[PublicIpReference] = ..., 
                subnet: Optional[SubnetReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.NsgReference(AzureResourceReference):
        source_arm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_arm_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.NsgSecurityRule(Model):
        access: str
        description: str
        destination_address_prefix: str
        destination_port_range: str
        direction: str
        name: str
        priority: int
        protocol: str
        source_address_prefix: str
        source_port_range: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access: Optional[str] = ..., 
                description: Optional[str] = ..., 
                destination_address_prefix: Optional[str] = ..., 
                destination_port_range: Optional[str] = ..., 
                direction: Optional[str] = ..., 
                name: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                protocol: Optional[str] = ..., 
                source_address_prefix: Optional[str] = ..., 
                source_port_range: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.OperationErrorAdditionalInfo(Model):
        info: MoveErrorInfo
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


    class azure.mgmt.resourcemover.models.OperationStatus(Model):
        end_time: str
        error: OperationStatusError
        id: str
        name: str
        properties: JSON
        start_time: str
        status: str

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


    class azure.mgmt.resourcemover.models.OperationStatusError(Model):
        additional_info: list[OperationErrorAdditionalInfo]
        code: str
        details: list[OperationStatusError]
        message: str

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


    class azure.mgmt.resourcemover.models.OperationsDiscovery(Model):
        display: Display
        is_data_action: bool
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[Display] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
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


    class azure.mgmt.resourcemover.models.OperationsDiscoveryCollection(Model):
        next_link: str
        value: list[OperationsDiscovery]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationsDiscovery]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.PrepareRequest(Model):
        move_resource_input_type: Union[str, MoveResourceInputType]
        move_resources: list[str]
        validate_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                move_resource_input_type: Optional[Union[str, MoveResourceInputType]] = ..., 
                move_resources: List[str], 
                validate_only: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.resourcemover.models.ProxyResourceReference(AzureResourceReference):
        name: str
        source_arm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                source_arm_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.PublicIPAddressResourceSettings(ResourceSettings):
        domain_name_label: str
        fqdn: str
        public_ip_allocation_method: str
        resource_type: str
        sku: str
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str
        zones: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_name_label: Optional[str] = ..., 
                fqdn: Optional[str] = ..., 
                public_ip_allocation_method: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                zones: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.PublicIpReference(AzureResourceReference):
        source_arm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_arm_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.RequiredForResourcesCollection(Model):
        source_ids: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.ResolutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.resourcemover.models.ResourceGroupResourceSettings(ResourceSettings):
        resource_type: str
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.resourcemover.models.ResourceMoveRequest(Model):
        move_resource_input_type: Union[str, MoveResourceInputType]
        move_resources: list[str]
        validate_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                move_resource_input_type: Optional[Union[str, MoveResourceInputType]] = ..., 
                move_resources: List[str], 
                validate_only: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.ResourceSettings(Model):
        resource_type: str
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.SqlDatabaseResourceSettings(ResourceSettings):
        resource_type: str
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str
        zone_redundant: Union[str, ZoneRedundant]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                zone_redundant: Optional[Union[str, ZoneRedundant]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.SqlElasticPoolResourceSettings(ResourceSettings):
        resource_type: str
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str
        zone_redundant: Union[str, ZoneRedundant]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                zone_redundant: Optional[Union[str, ZoneRedundant]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.SqlServerResourceSettings(ResourceSettings):
        resource_type: str
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.SubnetReference(ProxyResourceReference):
        name: str
        source_arm_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                source_arm_resource_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.SubnetResourceSettings(Model):
        address_prefix: str
        name: str
        network_security_group: NsgReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_prefix: Optional[str] = ..., 
                name: Optional[str] = ..., 
                network_security_group: Optional[NsgReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.Summary(Model):
        count: int
        item: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                item: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.SummaryCollection(Model):
        field_name: str
        summary: list[Summary]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                field_name: Optional[str] = ..., 
                summary: Optional[List[Summary]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.SystemData(Model):
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


    class azure.mgmt.resourcemover.models.TargetAvailabilityZone(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NA = "NA"
        ONE = "1"
        THREE = "3"
        TWO = "2"


    class azure.mgmt.resourcemover.models.UnresolvedDependenciesFilter(Model):
        properties: UnresolvedDependenciesFilterProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[UnresolvedDependenciesFilterProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.UnresolvedDependenciesFilterProperties(Model):
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


    class azure.mgmt.resourcemover.models.UnresolvedDependency(Model):
        count: int
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
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


    class azure.mgmt.resourcemover.models.UnresolvedDependencyCollection(Model):
        next_link: str
        summary_collection: SummaryCollection
        total_count: int
        value: list[UnresolvedDependency]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[UnresolvedDependency]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.UpdateMoveCollectionRequest(Model):
        identity: Identity
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
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


    class azure.mgmt.resourcemover.models.VirtualMachineResourceSettings(ResourceSettings):
        resource_type: str
        tags: dict[str, str]
        target_availability_set_id: str
        target_availability_zone: Union[str, TargetAvailabilityZone]
        target_resource_group_name: str
        target_resource_name: str
        target_vm_size: str
        user_managed_identities: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                target_availability_set_id: Optional[str] = ..., 
                target_availability_zone: Optional[Union[str, TargetAvailabilityZone]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                target_vm_size: Optional[str] = ..., 
                user_managed_identities: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.VirtualNetworkResourceSettings(ResourceSettings):
        address_space: list[str]
        dns_servers: list[str]
        enable_ddos_protection: bool
        resource_type: str
        subnets: list[SubnetResourceSettings]
        tags: dict[str, str]
        target_resource_group_name: str
        target_resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_space: Optional[List[str]] = ..., 
                dns_servers: Optional[List[str]] = ..., 
                enable_ddos_protection: Optional[bool] = ..., 
                subnets: Optional[List[SubnetResourceSettings]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_resource_group_name: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resourcemover.models.ZoneRedundant(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


namespace azure.mgmt.resourcemover.operations

    class azure.mgmt.resourcemover.operations.MoveCollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_bulk_remove(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[BulkRemoveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_bulk_remove(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_commit(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[CommitRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_commit(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_discard(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[DiscardRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_discard(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_initiate_move(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[ResourceMoveRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_initiate_move(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_prepare(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[PrepareRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_prepare(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def begin_resolve_dependencies(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[MoveCollection] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MoveCollection: ...

        @distributed_trace
        def list_move_collections_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[MoveCollection]: ...

        @distributed_trace
        def list_move_collections_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[MoveCollection]: ...

        @distributed_trace
        def list_required_for(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                source_id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> RequiredForResourcesCollection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[UpdateMoveCollectionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MoveCollection: ...


    class azure.mgmt.resourcemover.operations.MoveResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                body: Optional[MoveResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MoveResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MoveResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                move_resource_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> MoveResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[MoveResource]: ...


    class azure.mgmt.resourcemover.operations.OperationsDiscoveryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationsDiscoveryCollection: ...


    class azure.mgmt.resourcemover.operations.UnresolvedDependenciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                move_collection_name: str, 
                dependency_level: Optional[Union[str, DependencyLevel]] = None, 
                orderby: Optional[str] = None, 
                filter: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[UnresolvedDependency]: ...


```