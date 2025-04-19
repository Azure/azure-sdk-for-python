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
from .. import BlobStorage


if TYPE_CHECKING:
    from ...._extension import RoleAssignment
    from ....resourcegroup import ResourceGroup
    from .types import ContainerResource

    from azure.core.credentials import SupportsTokenInfo
    from azure.core.credentials_async import AsyncSupportsTokenInfo
    from azure.storage.blob import ContainerClient
    from azure.storage.blob.aio import ContainerClient as AsyncContainerClient


class ContainerKwargs(TypedDict, total=False):
    default_encryption_scope: str
    """Default the container to use specified encryption scope for all writes."""
    deny_encryption_scope_override: bool
    """Block override of encryption scope from the container default."""
    enable_nfsv3_all_squash: bool
    """Enable NFSv3 all squash on blob container."""
    enable_nfsv3_root_squash: bool
    """Enable NFSv3 root squash on blob container."""
    # immutability_policy_name: str
    # """Name of the immutable policy."""
    # immutability_policy_properties: Dict[str, object]
    # """Configure immutability policy."""
    immutable_storage_with_versioning_enabled: bool
    """This is an immutable property, when set to true it enables object level immutability at the container level.
    The property is immutable and can only be set to true at the container creation time. Existing containers must
    undergo a migration process.
    """
    metadata: Dict[str, str]
    """A name-value pair to associate with the container as metadata."""
    public_access: Literal["Blob", "Container", "None"]
    """Specifies whether data in the container may be accessed publicly and the level of access."""
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
                    "Storage Blob Data Contributor",
                    "Storage Blob Data Owner",
                    "Storage Blob Data Reader",
                    "Storage Blob Delegator",
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
                    "Storage Blob Data Contributor",
                    "Storage Blob Data Owner",
                    "Storage Blob Data Reader",
                    "Storage Blob Delegator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array or role assignments to create for user principal ID"""


_DEFAULT_CONTAINER: "ContainerResource" = {"name": GLOBAL_PARAMS["defaultName"]}
_DEFAULT_CONTAINER_EXTENSIONS: ExtensionResources = {
    "managed_identity_roles": ["Storage Blob Data Contributor"],
    "user_roles": ["Storage Blob Data Contributor"],
}
ContainerResourceType = TypeVar("ContainerResourceType", bound=Mapping[str, Any], default="ContainerResource")
ClientType = TypeVar("ClientType", default="ContainerClient")


class BlobContainer(_ClientResource, Generic[ContainerResourceType]):
    DEFAULTS: "ContainerResource" = _DEFAULT_CONTAINER  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_CONTAINER_EXTENSIONS
    properties: ContainerResourceType
    parent: BlobStorage  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["ContainerResource"] = None,
        /,
        name: Optional[str] = None,
        account: Optional[Union[str, Parameter, BlobStorage]] = None,
        **kwargs: Unpack["ContainerKwargs"],
    ) -> None:
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        if isinstance(account, BlobStorage):
            parent = account
        else:
            # 'parent' is passed by the reference classmethod.
            parent = kwargs.pop("parent", BlobStorage(account=account))  # type: ignore[typeddict-item]
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "default_encryption_scope" in kwargs:
                properties["properties"]["defaultEncryptionScope"] = kwargs.pop("default_encryption_scope")
            if "deny_encryption_scope_override" in kwargs:
                properties["properties"]["denyEncryptionScopeOverride"] = kwargs.pop("deny_encryption_scope_override")
            if "enable_nfsv3_all_squash" in kwargs:
                properties["properties"]["enableNfsV3AllSquash"] = kwargs.pop("enable_nfsv3_all_squash")
            if "enable_nfsv3_root_squash" in kwargs:
                properties["properties"]["enableNfsV3RootSquash"] = kwargs.pop("enable_nfsv3_root_squash")
            if "immutable_storage_with_versioning_enabled" in kwargs:
                properties["properties"]["immutableStorageWithVersioning"] = {
                    "enabled": kwargs.pop("immutable_storage_with_versioning_enabled")
                }
            if "metadata" in kwargs:
                properties["properties"]["metadata"] = kwargs.pop("metadata")
            if "public_access" in kwargs:
                properties["properties"]["publicAccess"] = kwargs.pop("public_access")

        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="containers",
            service_prefix=["blob_container"],
            identifier=ResourceIdentifiers.blob_container,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.Storage/storageAccounts/blobServices/containers"]:
        return "Microsoft.Storage/storageAccounts/blobServices/containers"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        account: Optional[Union[str, Parameter, BlobStorage[ResourceReference]]] = None,
        resource_group: Optional[Union[str, Parameter, "ResourceGroup[ResourceReference]"]] = None,
    ) -> "BlobContainer[ResourceReference]":
        parent: Optional[BlobStorage[ResourceReference]] = None
        if isinstance(account, (str, Parameter)):
            parent = BlobStorage.reference(
                account=account,
                resource_group=resource_group,
            )
        else:
            parent = account
        existing = super().reference(name=name, parent=parent)
        return cast(BlobContainer[ResourceReference], existing)

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        suffix_str = ""
        account_name = self.parent.parent.properties.get("name")
        if account_name:
            suffix_str += f"_{clean_name(account_name).lower()}"
        if suffix:
            suffix_str += f"_{clean_name(suffix).lower()}"
        return ResourceSymbol(f"container{suffix_str}")

    def _build_endpoint(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        name = self.parent.parent._settings["name"]  # pylint: disable=protected-access
        return (
            f"https://{name(config_store=config_store)}.blob.core.windows.net"
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
                f"AZURE_BLOB_CONTAINER_ENDPOINT{suffix}",
                Output("", "properties.primaryEndpoints.blob", parents[-1]).format() + outputs["name"][0].format(),
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
    ) -> "ContainerClient": ...
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
    ) -> "AsyncContainerClient": ...
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
                from azure.storage.blob.aio import ContainerClient as AsyncContainerClient

                cls = cast(Type, AsyncContainerClient.from_container_url)
            else:
                from azure.storage.blob import ContainerClient as SyncContainerClient

                cls = cast(Type, SyncContainerClient.from_container_url)
                use_async = False
        elif cls.__name__ == "ContainerClient" and hasattr(cls, "from_container_url"):
            if use_async is None:
                use_async = inspect.iscoroutinefunction(getattr(cls, "close"))
            # We know the attribute is present.
            cls = cast(Type, cls.from_container_url)  # type: ignore[reportFunctionMemberAccess, attr-defined]
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
