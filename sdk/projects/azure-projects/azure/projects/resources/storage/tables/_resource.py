# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    Tuple,
    Type,
    Union,
    Optional,
    Any,
    cast,
    overload,
)
from typing_extensions import TypeVar, Unpack

from ..._identifiers import ResourceIdentifiers
from ...resourcegroup import ResourceGroup
from ...._bicep.expressions import Output, ResourceSymbol, Parameter
from ...._resource import _ClientResource, ExtensionResources, ResourceReference
from .._resource import StorageAccount, StorageAccountKwargs

if TYPE_CHECKING:
    from .types import TableServiceResource, TablesCorsRule

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.data.tables import TableServiceClient
    from azure.data.tables.aio import TableServiceClient as AsyncTableServiceClient


class TableStorageKwargs(StorageAccountKwargs, total=False):
    cors_rules: Union[List[Union["TablesCorsRule", Parameter]], Parameter]
    """Specifies CORS rules for the Table service. You can include up to five CorsRule elements in the request.
    If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be
    disabled for the Table service.
    """


_DEFAULT_TABLE_SERVICE: "TableServiceResource" = {"name": "default"}
_DEFAULT_TABLE_SERVICE_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": ["Storage Table Data Contributor"],
    "user_roles": ["Storage Table Data Contributor"],
}
TableServiceResourceType = TypeVar("TableServiceResourceType", bound=Mapping[str, Any], default="TableServiceResource")
ClientType = TypeVar("ClientType", default="TableServiceClient")


class TableStorage(_ClientResource, Generic[TableServiceResourceType]):
    DEFAULTS: "TableServiceResource" = _DEFAULT_TABLE_SERVICE  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_TABLE_SERVICE_EXTENSIONS
    properties: TableServiceResourceType  # type: ignore[reportIncompatibleVariableOverride]
    parent: StorageAccount  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["TableServiceResource"] = None,
        /,
        account: Optional[Union[str, StorageAccount, Parameter]] = None,
        **kwargs: Unpack["TableStorageKwargs"],
    ) -> None:
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if "cors_rules" in kwargs:
                properties["properties"]["cors"] = {"corsRules": kwargs.pop("cors_rules")}

        if account and "parent" in kwargs:
            raise ValueError("Cannot specify both 'account' and 'parent'.")
        # 'parent' is passed by the reference classmethod.
        parent = kwargs.pop("parent", None)  # type: ignore[typeddict-item]
        if not parent:
            if isinstance(account, StorageAccount):
                parent = account
            else:
                # Tables kwargs have already been popped.
                parent = StorageAccount(name=account, **kwargs)  # type: ignore[misc]
                for key in StorageAccountKwargs.__annotations__:
                    kwargs.pop(key, None)  # type: ignore[misc]  # Not using string literal key.

        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="tableServices",
            service_prefix=["tables", "storage"],
            identifier=ResourceIdentifiers.table_storage,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.Storage/storageAccounts/tableServices"]:
        return "Microsoft.Storage/storageAccounts/tableServices"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        account: Union[str, Parameter, StorageAccount[ResourceReference]],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "TableStorage[ResourceReference]":
        parent: Optional[StorageAccount[ResourceReference]] = None
        if isinstance(account, (str, Parameter)):
            parent = StorageAccount.reference(
                name=account,
                resource_group=resource_group,
            )
        elif isinstance(account, StorageAccount) and resource_group:
            raise ValueError("Cannot provide a 'StorageAccount' instance with 'resource_group' value.")
        else:
            parent = account
        existing = super().reference(parent=parent)
        existing._settings["name"].set_value("default")  # pylint: disable=protected-access
        return cast(TableStorage[ResourceReference], existing)

    def __repr__(self) -> str:
        name = f'\'{self.parent.properties["name"]}\'' if "name" in self.parent.properties else "<default>"
        return f"{self.__class__.__name__}({name})"

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        return super()._build_symbol(self.parent.properties.get("name"))

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        return f"https://{self.parent._settings['name'](config_store=config_store)}.table.core.windows.net/"  # pylint: disable=protected-access

    def _get_default_name(self, *, config_store: Optional[Mapping[str, Any]]) -> str:  # pylint: disable=unused-argument
        return "default"

    def _outputs(  # type: ignore[override]  # Parameter subset
        self, *, parents: Tuple[ResourceSymbol, ...], suffix: str, **kwargs
    ) -> Dict[str, List[Output]]:
        return {
            "endpoint": [
                Output(
                    f"AZURE_TABLES_ENDPOINT{suffix}",
                    "properties.primaryEndpoints.table",
                    parents[0],
                )
            ]
        }

    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[Literal[False]] = None,
        **client_options,
    ) -> "TableServiceClient": ...
    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Literal[True],
        **client_options,
    ) -> "AsyncTableServiceClient": ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[False] = False,
        **client_options,
    ) -> ClientType: ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Optional[Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]] = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[bool] = None,
        return_credential: Literal[True],
        **client_options,
    ) -> Tuple[ClientType, Union["SupportsTokenInfo", "AsyncSupportsTokenInfo"]]: ...
    def get_client(
        self,
        cls=None,
        /,
        *,
        transport=None,
        credential=None,
        api_version=None,
        audience=None,
        config_store=None,
        use_async=None,
        return_credential=False,
        **client_options,
    ):
        if cls is None:
            if use_async:
                from azure.data.tables.aio import TableServiceClient as AsyncTableServiceClient

                cls = AsyncTableServiceClient
            else:
                from azure.data.tables import TableServiceClient as SyncTableServiceClient

                cls = SyncTableServiceClient
                use_async = False
        return super().get_client(
            cls,
            transport=transport,
            credential=credential,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            use_async=use_async,
            return_credential=return_credential,
            **client_options,
        )
