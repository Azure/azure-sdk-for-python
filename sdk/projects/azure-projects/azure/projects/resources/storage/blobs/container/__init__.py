# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from collections import defaultdict
import inspect
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    Literal,
    Mapping,
    Tuple,
    TypedDict,
    Union,
    overload,
    Optional,
    Any,
    Type,
)
from typing_extensions import TypeVar, Unpack

from ....._component import ComponentField
from ....._parameters import GLOBAL_PARAMS
from ...._identifiers import ResourceIdentifiers
from ....._bicep.expressions import Output, Parameter, ResourceSymbol, Expression
from ....._resource import Resource, _ClientResource, _build_envs, ExtensionResources, ResourceReference
from .. import BlobStorage


if TYPE_CHECKING:
    from ...._extension import RoleAssignment
    from ....resourcegroup import ResourceGroup
    from .types import ContainerResource
    from azure.storage.blob import ContainerClient


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
    """This is an immutable property, when set to true it enables object level immutability at the container level. The property is immutable and can only be set to true at the container creation time. Existing containers must undergo a migration process."""
    metadata: Dict[str, object]
    """A name-value pair to associate with the container as metadata."""
    public_access: Literal["Blob", "Container", "None"]
    """Specifies whether data in the container may be accessed publicly and the level of access."""
    roles: Union[
        Parameter[List[Union["RoleAssignment", str]]],
        List[
            Union[
                Parameter[Union[str, "RoleAssignment"]],
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
        Parameter[List[Union["RoleAssignment", str]]],
        List[
            Union[
                Parameter[Union[str, "RoleAssignment"]],
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
_DEFAULT_CONTAINER_EXTENSIONS: ExtensionResources = {}
ContainerResourceType = TypeVar("ContainerResourceType", default="ContainerResource")
ClientType = TypeVar("ClientType", default="ContainerClient")


class BlobContainer(_ClientResource[ContainerResourceType]):
    DEFAULTS: "ContainerResource" = _DEFAULT_CONTAINER
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_CONTAINER_EXTENSIONS
    resource: Literal["Microsoft.Storage/storageAccounts/blobServices/containers"]
    properties: ContainerResourceType

    def __init__(
        self,
        properties: Optional["ContainerResource"] = None,
        /,
        name: Optional[str] = None,
        account: Optional[Union[str, Parameter[str], BlobStorage, ComponentField]] = None,
        **kwargs: Unpack["ContainerKwargs"],
    ) -> None:
        existing = kwargs.pop("existing", False)
        extensions: ExtensionResources = defaultdict(list)
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        parent = account if isinstance(account, BlobStorage) else kwargs.pop("parent", BlobStorage(account=account))
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
                properties["properties"]["immutableStorageWithVersioning"] = {}
                properties["properties"]["immutableStorageWithVersioning"]["enabled"] = kwargs.pop(
                    "immutable_storage_with_versioning_enabled"
                )
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
    def resource(self) -> str:
        if self._resource:
            return self._resource
        from .types import RESOURCE

        self._resource = RESOURCE
        return self._resource

    @property
    def version(self) -> str:
        if self._version:
            return self._version
        from .types import VERSION

        self._version = VERSION
        return self._version

    @classmethod
    def reference(
        cls,
        *,
        name: Union[str, Parameter[str]],
        account: Optional[Union[str, Parameter[str], BlobStorage]] = None,
        resource_group: Optional[Union[str, Parameter[str], "ResourceGroup"]] = None,
    ) -> "BlobContainer[ResourceReference]":
        from .types import RESOURCE, VERSION

        resource = f"{RESOURCE}@{VERSION}"
        if isinstance(account, (str, Parameter)):
            parent = BlobStorage.reference(
                account=account,
                resource_group=resource_group,
            )
        else:
            parent = account

        return super().reference(resource=resource, name=name, parent=parent)

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self.parent.parent._settings['name'](config_store=config_store)}.blob.core.windows.net/{self._settings['name'](config_store=config_store)}"

    def _outputs(
        self,
        *,
        symbol: ResourceSymbol,
        resource_group: Union[str, ResourceSymbol],
        parents: Tuple[ResourceSymbol, ...],
        **kwargs,
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, **kwargs)
        outputs["endpoint"] = Output(
            f"AZURE_BLOB_CONTAINER_ENDPOINT{self._suffix}",
            Output("", "properties.primaryEndpoints.blob", parents[-1]).format() + outputs["name"].format(),
        )
        return outputs

    def get_client(
        self,
        cls: Optional[Callable[..., ClientType]] = None,
        /,
        *,
        transport: Any = None,
        api_version: Optional[str] = None,
        audience: Optional[str] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        env_name: Optional[str] = None,
        use_async: Optional[bool] = None,
        **client_options,
    ) -> ClientType:
        if cls is None:
            if use_async:
                from azure.storage.blob.aio import ContainerClient

                cls = ContainerClient.from_container_url
            else:
                from azure.storage.blob import ContainerClient

                cls = ContainerClient.from_container_url
                use_async = False
        elif cls.__name__ == "ContainerClient":
            if use_async is None:
                use_async = inspect.iscoroutinefunction(getattr(cls, "close"))
            cls = cls.from_container_url
        return super().get_client(
            cls,
            transport=transport,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            env_name=env_name,
            use_async=use_async,
            **client_options,
        )
