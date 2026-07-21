```py
namespace azure.ai.agentserver.core.storage

    class azure.ai.agentserver.core.storage.DeletedStateStore(_Model):
        deleted: bool
        id: Optional[str]
        name: str
        object: Literal[StateStoreObjectType.STATE_STORE]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: Optional[str] = ..., 
                name: str, 
                object: Literal[StateStoreObjectType.STATE_STORE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.DeletedStateStoreItem(_Model):
        deleted: bool
        id: Optional[str]
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: Optional[str] = ..., 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStateStore(FoundryStorageClient): implements AsyncContextManager 
        property name: str    # Read-only

        def __init__(
                self, 
                name: str, 
                credential: AsyncTokenCredential | None = None, 
                endpoint: FoundryStorageEndpoint | str | None = None, 
                *, 
                api_version: str = "v1", 
                description: str | None = ..., 
                item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS, 
                tags: Mapping[str, str] | None = ..., 
                user_id: str | None = ..., 
                user_isolation: bool = False, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        async def get_or_create(
                cls, 
                name: str, 
                credential: AsyncTokenCredential | None = None, 
                endpoint: FoundryStorageEndpoint | str | None = None, 
                *, 
                api_version: str = "v1", 
                description: str | None = ..., 
                item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS, 
                tags: Mapping[str, str] | None = ..., 
                user_id: str | None = ..., 
                user_isolation: bool = False, 
                **kwargs: Any
            ) -> FoundryStateStore: ...

        async def aclose(self) -> None: ...

        async def create_item(
                self, 
                key: str, 
                value: JSONObject, 
                *, 
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemRef: ...

        async def delete(self) -> DeletedStateStore: ...

        async def delete_item(
                self, 
                key: str, 
                *, 
                if_match: str | None = ...
            ) -> DeletedStateStoreItem: ...

        async def get(self) -> StateStore: ...

        async def get_item(self, key: str) -> StateStoreItem | None: ...

        async def list_keys(
                self, 
                *, 
                after: str | None = ..., 
                before: str | None = ..., 
                limit: int | None = ..., 
                order: Order = "desc", 
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemKeyPage: ...

        async def set_item(
                self, 
                key: str, 
                value: JSONObject, 
                *, 
                if_match: str | None = ..., 
                require_exists: bool = False, 
                tags: Mapping[str, str] | None = ...
            ) -> StateStoreItemRef: ...

        async def update(
                self, 
                *, 
                description: str | None | object = _UNSET, 
                tags: Mapping[str, str] | None | object = _UNSET
            ) -> StateStore: ...


    class azure.ai.agentserver.core.storage.FoundryStorageApiError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageBadRequestError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                param: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageClient: implements AsyncContextManager 

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                endpoint: FoundryStorageEndpoint, 
                *, 
                get_server_version: Callable[[], str] | None = ..., 
                sdk_moniker: str | None = ..., 
                **kwargs: Any
            ) -> None: ...

        async def aclose(self) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageConflictError(FoundryStorageBadRequestError):

        def __init__(
                self, 
                message: str, 
                *, 
                param: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageEndpoint:

        def __init__(
                self, 
                *, 
                api_version: str = _DEFAULT_API_VERSION, 
                storage_base_url: str
            ) -> None: ...

        @classmethod
        def from_endpoint(
                cls, 
                endpoint: str, 
                *, 
                api_version: str = _DEFAULT_API_VERSION
            ) -> FoundryStorageEndpoint: ...

        @classmethod
        def from_env(
                cls, 
                *, 
                api_version: str = _DEFAULT_API_VERSION
            ) -> FoundryStorageEndpoint: ...

        def build_url(
                self, 
                path: str, 
                **extra_params: str
            ) -> str: ...


    class azure.ai.agentserver.core.storage.FoundryStorageError(Exception):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStorageNotFoundError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.FoundryStoragePreconditionError(FoundryStorageError):

        def __init__(
                self, 
                message: str, 
                *, 
                current_etag: str | None = ..., 
                response_body: dict[str, Any] | None = ..., 
                status_code: int | None = ...
            ) -> None: ...


    class azure.ai.agentserver.core.storage.StateStore(_Model):
        created_at: int
        description: Optional[str]
        id: str
        item_ttl_seconds: int
        name: str
        object: Literal[StateStoreObjectType.STATE_STORE]
        tags: Optional[dict[str, str]]
        updated_at: int
        user_isolation: bool

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                description: Optional[str] = ..., 
                id: str, 
                item_ttl_seconds: int, 
                name: str, 
                object: Literal[StateStoreObjectType.STATE_STORE], 
                tags: Optional[dict[str, str]] = ..., 
                updated_at: int, 
                user_isolation: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.StateStoreItem(_Model):
        created_at: int
        etag: str
        id: str
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
        tags: Optional[dict[str, str]]
        updated_at: int
        value: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                etag: str, 
                id: str, 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM], 
                tags: Optional[dict[str, str]] = ..., 
                updated_at: int, 
                value: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.core.storage.StateStoreItemKey(_Model):
        created_at: int
        etag: str
        id: str
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
        tags: Optional[dict[str, str]]
        updated_at: int

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                etag: str, 
                id: str, 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM], 
                tags: Optional[dict[str, str]] = ..., 
                updated_at: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    @dataclass(eq = True, frozen = False, init = True, kw_only = False, match_args = True, order = False, repr = True, slots = False, unsafe_hash = False, weakref_slot = False)
    class azure.ai.agentserver.core.storage.StateStoreItemKeyPage:
        first_id: Optional[str]
        has_more: bool = field(compare = True, default = False, hash = None, init = True, kw_only = False, metadata = {}, name = "has_more", repr = True, type = "bool")
        keys: list[StateStoreItemKey]
        last_id: Optional[str]

        def __eq__() -> None: ...

        def __init__(
                keys: list, 
                first_id: str | None, 
                last_id: str | None, 
                has_more: bool
            ): ...

        def __repr__() -> None: ...


    class azure.ai.agentserver.core.storage.StateStoreItemRef(_Model):
        created_at: int
        etag: str
        id: str
        key: str
        object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM]
        updated_at: int

        @overload
        def __init__(
                self, 
                *, 
                created_at: int, 
                etag: str, 
                id: str, 
                key: str, 
                object: Literal[StateStoreItemObjectType.STATE_STORE_ITEM], 
                updated_at: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```