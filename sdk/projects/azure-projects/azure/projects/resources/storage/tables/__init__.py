from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Tuple, Union, Unpack, Optional, Any
from typing_extensions import TypeVar

from ..._identifiers import ResourceIdentifiers
from ...resourcegroup import ResourceGroup
from ...._bicep.expressions import Output, ResourceSymbol, Parameter
from ...._resource import _ClientResource, ExtensionResources, ResourceReference
from .. import StorageAccount, StorageAccountKwargs

if TYPE_CHECKING:
    from .types import TableServiceResource, CorsRule
    from azure.data.tables import TableServiceClient


class TableStorageKwargs(StorageAccountKwargs):
    cors_rules: Union[List[Union['CorsRule', Parameter['CorsRule']]], Parameter[List['CorsRule']]]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Blob service."""


_DEFAULT_TABLE_SERVICE: 'TableServiceResource' = {'name': 'default'}
_DEFAULT_TABLE_SERVICE_EXTENSIONS: ExtensionResources = {
    'managed_identity_roles': ['Storage Table Data Contributor'],
    'user_roles': ['Storage Table Data Contributor']
}
TableServiceResourceType = TypeVar('TableServiceResourceType', default='TableServiceResource')
ClientType = TypeVar("ClientType", default='TableServiceClient')
 


class TableStorage(_ClientResource[TableServiceResourceType]):
    DEFAULTS: 'TableServiceResource' = _DEFAULT_TABLE_SERVICE
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_TABLE_SERVICE_EXTENSIONS
    resource: Literal["Microsoft.Storage/storageAccounts/tableServices"]
    properties: TableServiceResourceType

    def __init__(
            self,
            properties: Optional['TableServiceResource'] = None,
            /,
            account: Optional[Union[str, StorageAccount, Parameter[str]]] = None,
            **kwargs: Unpack['TableStorageKwargs']
    ) -> None:
        existing = kwargs.pop('existing', False)
        extensions: ExtensionResources = defaultdict(list)
        if 'roles' in kwargs:
            extensions['managed_identity_roles'] = kwargs.pop('roles')
        if 'user_roles' in kwargs:
            extensions['user_roles'] = kwargs.pop('user_roles')
        if not existing:
            properties = properties or {}
            if 'properties' not in properties:
                properties['properties'] = {}
            if 'cors_rules' in kwargs:
                properties['properties']['cors'] = {}
                properties['properties']['cors']['corsRules'] = kwargs.pop('cors_rules')

        parent = kwargs.pop('parent', None)
        if account and 'parent' in kwargs:
            raise ValueError("Cannot specify both 'account' and 'parent'.")
        if not parent:
            parent = account if isinstance(account, StorageAccount) else StorageAccount(name=account, **kwargs)
            for key in StorageAccountKwargs.__optional_keys__:
                kwargs.pop(key, None)

        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="tableServices",
            service_prefix=["tables", "storage"],
            identifier=ResourceIdentifiers.table_storage,
            **kwargs
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
            account: Union[str, Parameter[str], StorageAccount],
            resource_group: Optional[Union[str, Parameter[str], ResourceGroup]] = None,
    ) -> 'TableStorage[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        if isinstance(account, (str, Parameter)):
            parent = StorageAccount.reference(
                name=account,
                resource_group=resource_group,
            )
        elif isinstance(account, StorageAccount) and resource_group:
            raise ValueError("Cannot provide a 'StorageAccount' instance with 'resource_group' value.")
        else:
            parent = account
        existing = super().reference(
            resource=resource,
            parent=parent,
        )
        existing._settings['name'].set_value('default')
        return existing

    def __repr__(self) -> str:
        name = f'\'{self.parent.properties["name"]}\'' if 'name' in self.parent.properties else "<default>"
        return f"{self.__class__.__name__}({name})"

    def _build_endpoint(self, *, config_store: Mapping[str, Any]) -> str:
        return f"https://{self.parent._settings['name'](config_store=config_store)}.table.core.windows.net/"

    def _outputs(
            self,
            *,
            parents: Tuple[ResourceSymbol, ...],
            **kwargs
    ) -> Dict[str, Output]:
        return {'endpoint': Output(f"AZURE_TABLES_ENDPOINT{self.parent._suffix}", "properties.primaryEndpoints.table", parents[0])}

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
                from azure.data.tables.aio import TableServiceClient
                cls = TableServiceClient
            else:
                from azure.data.tables import TableServiceClient
                cls = TableServiceClient
                use_async = False
        return super().get_client(
            cls,
            transport=transport,
            api_version=api_version,
            audience=audience,
            config_store=config_store,
            env_name=env_name,
            **client_options
        )
