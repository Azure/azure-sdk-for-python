```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resource.locks

    class azure.mgmt.resource.locks.ManagementLockClient: implements ContextManager 
        authorization_operations: AuthorizationOperationsOperations
        management_locks: ManagementLocksOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.resource.locks.aio

    class azure.mgmt.resource.locks.aio.ManagementLockClient: implements AsyncContextManager 
        authorization_operations: AuthorizationOperationsOperations
        management_locks: ManagementLocksOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.resource.locks.aio.operations

    class azure.mgmt.resource.locks.aio.operations.AuthorizationOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.resource.locks.aio.operations.ManagementLocksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        async def create_or_update_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        async def create_or_update_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        async def create_or_update_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        async def create_or_update_at_subscription_level(
                self, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        async def create_or_update_at_subscription_level(
                self, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        async def create_or_update_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace_async
        async def delete_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_at_subscription_level(
                self, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace_async
        async def get_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace_async
        async def get_at_subscription_level(
                self, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace_async
        async def get_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace
        def list_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagementLockObject]: ...

        @distributed_trace
        def list_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagementLockObject]: ...

        @distributed_trace
        def list_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagementLockObject]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagementLockObject]: ...


namespace azure.mgmt.resource.locks.models

    class azure.mgmt.resource.locks.models.LockLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAN_NOT_DELETE = "CanNotDelete"
        NOT_SPECIFIED = "NotSpecified"
        READ_ONLY = "ReadOnly"


    class azure.mgmt.resource.locks.models.ManagementLockListResult(Model):
        next_link: str
        value: list[ManagementLockObject]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[ManagementLockObject]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.locks.models.ManagementLockObject(Model):
        id: str
        level: Union[str, LockLevel]
        name: str
        notes: str
        owners: list[ManagementLockOwner]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                level: Union[str, LockLevel], 
                notes: Optional[str] = ..., 
                owners: Optional[list[ManagementLockOwner]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.locks.models.ManagementLockOwner(Model):
        application_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.locks.models.Operation(Model):
        display: OperationDisplay
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.locks.models.OperationDisplay(Model):
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.resource.locks.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.resource.locks.operations

    class azure.mgmt.resource.locks.operations.AuthorizationOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.resource.locks.operations.ManagementLocksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        def create_or_update_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        def create_or_update_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        def create_or_update_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        def create_or_update_at_subscription_level(
                self, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        def create_or_update_at_subscription_level(
                self, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                parameters: ManagementLockObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @overload
        def create_or_update_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace
        def delete_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_at_subscription_level(
                self, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_at_resource_group_level(
                self, 
                resource_group_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace
        def get_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace
        def get_at_subscription_level(
                self, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace
        def get_by_scope(
                self, 
                scope: str, 
                lock_name: str, 
                **kwargs: Any
            ) -> ManagementLockObject: ...

        @distributed_trace
        def list_at_resource_group_level(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ManagementLockObject]: ...

        @distributed_trace
        def list_at_resource_level(
                self, 
                resource_group_name: str, 
                resource_provider_namespace: str, 
                parent_resource_path: str, 
                resource_type: str, 
                resource_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ManagementLockObject]: ...

        @distributed_trace
        def list_at_subscription_level(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ManagementLockObject]: ...

        @distributed_trace
        def list_by_scope(
                self, 
                scope: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ManagementLockObject]: ...


```