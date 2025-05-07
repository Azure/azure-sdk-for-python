# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
import inspect
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
from typing_extensions import TypeVar, Unpack, TypedDict

from ....._parameters import GLOBAL_PARAMS
from ...._identifiers import ResourceIdentifiers
from ....._bicep.expressions import Output, Parameter, ResourceSymbol
from ....._bicep.utils import clean_name
from ....._resource import _ClientResource, ExtensionResources, ResourceReference
from .. import TableStorage


if TYPE_CHECKING:
    from ...._extension import RoleAssignment
    from ....resourcegroup import ResourceGroup
    from .types import TableResource

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.data.tables import TableClient
    from azure.data.tables.aio import TableClient as AsyncTableClient


class TableKwargs(TypedDict, total=False):
    roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Reader and Data Access",
                    "Role Based Access Control Administrator",
                    "Storage Account Backup Contributor",
                    "Storage Account Contributor",
                    "Storage Account Key Operator Service Role",
                    "Storage Table Data Contributor",
                    "Storage Table Data Reader",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create for user-assigned identity."""
    user_roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Reader and Data Access",
                    "Role Based Access Control Administrator",
                    "Storage Account Backup Contributor",
                    "Storage Account Contributor",
                    "Storage Account Key Operator Service Role",
                    "Storage Table Data Contributor",
                    "Storage Table Data Reader",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array or role assignments to create for user principal ID"""


_DEFAULT_TABLE: "TableResource" = {"name": GLOBAL_PARAMS["defaultName"]}
_DEFAULT_TABLE_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": ["Storage Blob Data Contributor"],
    "user_roles": ["Storage Blob Data Contributor"],
}
TableResourceType = TypeVar("TableResourceType", bound=Mapping[str, Any], default="TableResource")
ClientType = TypeVar("ClientType", default="TableClient")


class Table(_ClientResource, Generic[TableResourceType]):
    DEFAULTS: "TableResource" = _DEFAULT_TABLE  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_TABLE_EXTENSIONS
    properties: TableResourceType
    parent: TableStorage  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["TableResource"] = None,
        /,
        name: Optional[str] = None,
        account: Optional[Union[str, Parameter, TableStorage]] = None,
        **kwargs: Unpack["TableKwargs"],
    ) -> None:
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        if isinstance(account, TableStorage):
            parent = account
        else:
            # 'parent' is passed by the reference classmethod.
            parent = kwargs.pop("parent", TableStorage(account=account))  # type: ignore[typeddict-item]
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name

        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="tables",
            service_prefix=["table"],
            identifier=ResourceIdentifiers.table,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.Storage/storageAccounts/tableServices/tables"]:
        return "Microsoft.Storage/storageAccounts/tableServices/tables"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        account: Optional[Union[str, Parameter, TableStorage[ResourceReference]]] = None,
        resource_group: Optional[Union[str, Parameter, "ResourceGroup[ResourceReference]"]] = None,
    ) -> "Table[ResourceReference]":
        parent: Optional[TableStorage[ResourceReference]] = None
        if isinstance(account, (str, Parameter)):
            parent = TableStorage.reference(
                account=account,
                resource_group=resource_group,
            )
        else:
            parent = account
        existing = super().reference(name=name, parent=parent)
        return cast(Table[ResourceReference], existing)

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        suffix_str = ""
        account_name = self.parent.parent.properties.get("name")
        if account_name:
            suffix_str += f"_{clean_name(account_name).lower()}"
        if suffix:
            suffix_str += f"_{clean_name(suffix).lower()}"
        return ResourceSymbol(f"table{suffix_str}")

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        name = self.parent.parent._settings["name"]  # pylint: disable=protected-access
        return (
            f"https://{name(config_store=config_store)}.table.core.windows.net"
            + f"/{self._settings['name'](config_store=config_store)}"
        )

    def _outputs(  # type: ignore[override]  # Parameter subset
        self,
        *,
        symbol: ResourceSymbol,
        suffix: str,
        parents: Tuple[ResourceSymbol, ...],
        **kwargs,
    ) -> Dict[str, List[Output]]:
        outputs = super()._outputs(symbol=symbol, suffix=suffix, **kwargs)
        outputs["endpoint"].append(
            Output(
                f"AZURE_TABLE_ENDPOINT{suffix}",
                Output("", "properties.primaryEndpoints.table", parents[-1]).format() + outputs["name"][0].format(),
            )
        )
        return outputs

    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Optional[Literal[False]] = None,
        **client_options,
    ) -> "TableClient": ...
    @overload
    def get_client(
        self,
        /,
        *,
        transport: Any = None,
        credential: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        use_async: Literal[True],
        **client_options,
    ) -> "AsyncTableClient": ...
    @overload
    def get_client(
        self,
        cls: Type[ClientType],
        /,
        *,
        transport: Any = None,
        credential: Any = None,
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
        credential: Any = None,
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
                from azure.data.tables.aio import TableClient as AsyncTableClient

                cls = cast(Type, AsyncTableClient.from_table_url)
            else:
                from azure.data.tables import TableClient as SyncTableClient

                cls = cast(Type, SyncTableClient.from_table_url)
                use_async = False
        elif cls.__name__ == "TableClient" and hasattr(cls, "from_table_url"):
            if use_async is None:
                use_async = inspect.iscoroutinefunction(getattr(cls, "close"))
            # We know the attribute is present.
            cls = cast(Type, cls.from_table_url)  # type: ignore[reportFunctionMemberAccess, attr-defined]
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
