from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Literal, Mapping, Tuple, TypedDict, Union, Unpack, Optional, overload
from typing_extensions import TypeVar

from azure.core.credentials import SupportsTokenInfo
from azure.core.credentials_async import AsyncSupportsTokenInfo

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from .._extension import ManagedIdentity, convert_managed_identities, RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._setting import StoredPrioritizedSetting
from ..._bicep.expressions import Guid, Expression, ResourceSymbol, Parameter, ResourceGroup, Output
from ..._resource import Resource, FieldsType, FieldType, ResourceReference, ExtensionResources, _build_envs, _load_dev_environment
from ._connection import AIConnection

if TYPE_CHECKING:
    from .types import MachineLearningWorkspaceResource
    from azure.ai.projects import AIProjectClient


class MachineLearningWorkspaceKwargs(TypedDict, total=False):
    """"""
    friendly_name: Union[str, Parameter[str]]
    """"""
    sku: Literal['Basic', 'Free', 'Premium', 'Standard']
    """Specifies the SKU, also referred as 'edition' of the Azure Machine Learning workspace."""
    application_insights: str
    """The resource ID of the associated Application Insights. Required if 'kind' is 'Default' or 'FeatureStore'."""
    keyvault: str
    """The resource ID of the associated Key Vault. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    storage: str
    """The resource ID of the associated Storage Account. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    feature_store_settings: 'FeatureStoreSetting'
    """Settings for feature store type workspaces. Required if 'kind' is set to 'FeatureStore'."""
    hub: str
    """The resource ID of the hub to associate with the workspace. Required if 'kind' is set to 'Project'."""
    primary_user_assigned_identity: str
    """The user assigned identity resource ID that represents the workspace identity. Required if 'userAssignedIdentities' is not empty and may not be used if 'systemAssignedIdentity' is enabled."""
    container_registry: str
    """The resource ID of the associated Container Registry."""
    description: str
    """The description of this workspace."""
    # diagnostic_settings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    discovery_url: str
    """URL for the discovery service to identify regional endpoints for machine learning experimentation services."""
    hbi_workspace: bool
    """The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service."""
    image_build_compute: str
    """The compute name for image build."""
    location: str
    """Location for all resources."""
    # lock: 'Lock'
    # """The lock settings of the service."""
    managed_identities: 'ManagedIdentity'
    """The managed identity definition for this resource. At least one identity type is required."""
    managed_network: 'ManagedNetworkSetting'
    """Managed Network settings for a machine learning workspace."""
    # private_endpoints: List['PrivateEndpoint']
    # """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    public_network_access: Literal['Disabled', 'Enabled']
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled."""
    roles: Union[Parameter[List[Union[str, 'RoleAssignment']]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', Literal['AzureML Compute Operator', 'AzureML Data Scientist', 'AzureML Metrics Writer (preview)', 'AzureML Registry User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]]]
    """Array of role assignments to create."""
    user_roles: Union[Parameter[List[Union[str, 'RoleAssignment']]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', Literal['AzureML Compute Operator', 'AzureML Data Scientist', 'AzureML Metrics Writer (preview)', 'AzureML Registry User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]]]
    """Array of Role assignments to create for user principal ID"""
    serverless_compute_settings: 'ServerlessComputeSetting'
    """Settings for serverless compute created in the workspace."""
    service_managed_resources_settings: Dict[str, object]
    """The service managed resource settings."""
    shared_private_link_resources: List[object]
    """The list of shared private link resources in this workspace. Note: This property is not idempotent."""
    system_datastores_auth_mode: Literal['accessKey', 'identity']
    """The authentication mode used by the workspace when connecting to the default storage account."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Tags of the resource."""
    workspacehub_config: 'WorkspaceHubConfig'
    """Configuration for workspace hub settings."""


MachineLearningWorkspaceResourceType = TypeVar('CognitiveServicesAccountResourceType', default='MachineLearningWorkspaceResource')
_DEFAULT_ML_WORKSPACE: 'MachineLearningWorkspaceResource' = {
    'name': GLOBAL_PARAMS['defaultName'],
    'location': GLOBAL_PARAMS['location'],
    'tags': GLOBAL_PARAMS['azdTags'],
    #'properties': {
    #    'primaryUserAssignedIdentity': GLOBAL_PARAMS['managedIdentityId'],
    #},
    'identity': {
        'type': 'UserAssigned',
        'userAssignedIdentities': {GLOBAL_PARAMS['managedIdentityId'].format(): {}}
    }
}
_DEFAULT_ML_WORKSPACE_EXTENSIONS: ExtensionResources = {
    'managed_identity_roles': [],
    'user_roles': []
}
class MLWorkspace(Resource[MachineLearningWorkspaceResourceType]):
    DEFAULTS: 'MachineLearningWorkspaceResource' = _DEFAULT_ML_WORKSPACE
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_ML_WORKSPACE_EXTENSIONS
    resource: Literal["Microsoft.MachineLearningServices/workspaces"]
    properties: MachineLearningWorkspaceResourceType

    def __init__(
            self,
            properties: Optional['MachineLearningWorkspaceResource'] = None,
            /,
            name: Optional[str] = None,
            *,
            kind: Union[Parameter[str], Literal['Default', 'FeatureStore', 'Hub', 'Project']],
            **kwargs: Unpack[MachineLearningWorkspaceKwargs]
    ) -> None:
        existing = kwargs.pop('existing', False)
        extensions: ExtensionResources = defaultdict(list)
        properties = properties or {}
        properties['kind'] = kind
        if 'roles' in kwargs:
            extensions['managed_identity_roles'] = kwargs.pop('roles')
        if 'user_roles' in kwargs:
            extensions['user_roles'] = kwargs.pop('user_roles')
        # TODO: Finish populating kwarg properties
        if not existing:
            if 'properties' not in properties:
                properties['properties'] = {}
            if name:
                properties['name'] = name
            if 'friendly_name' in kwargs:
                properties['properties']['friendlyName'] = kwargs.pop('friendly_name')
            if 'description' in kwargs:
                properties['properties']['description'] = kwargs.pop('description')
            if 'location' in kwargs:
                properties['location'] = kwargs.pop('location')
            if 'managed_identities' in kwargs:
                properties['identity'] = convert_managed_identities(kwargs.pop('managed_identities'))
            if 'public_network_access' in kwargs:
                properties['properties']['publicNetworkAccess'] = kwargs.pop('public_network_access')
            if 'sku' in kwargs:
                properties['sku'] = properties.get('sku', {})
                properties['sku']['name'] = kwargs.pop('sku')
                properties['sku']['tier'] = properties['sku']['name']
            if 'tags' in kwargs:
                properties['tags'] = kwargs.pop('tags')
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=kwargs.pop('service_prefix', [f"ml_{kind}"]),
            existing=existing,
            identifier=kwargs.pop('identifier', ResourceIdentifiers.ml_workspace),
            **kwargs
        )

    @classmethod
    def reference(
            cls,
            *,
            name: Union[str, Parameter[str]],
            resource_group: Optional[Union[str, Parameter[str], ResourceGroup]] = None,
    ) -> 'MLWorkspace[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        return super().reference(
            resource=resource,
            name=name,
            resource_group=resource_group,
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

    def _build_symbol(self) -> ResourceSymbol:
        symbol = super()._build_symbol()
        symbol._value = f"{self.properties['kind'].lower()}_" + symbol._value
        return symbol

    def _find_all_resource_match(
            self,
            fields: FieldsType,
            *,
            resource: Optional[str] = None,
            resource_group: Optional[ResourceSymbol] = None,
            name: Optional[Union[str, Expression]] = None,
            parent: Optional[ResourceSymbol] = None,
    ) -> Generator[FieldType, None, None]:
        check_resource = resource or self.resource
        for field in (f for f in reversed(list(fields.values())) if f.resource == check_resource):
            if not resource and field.properties['kind'] != self.properties['kind']:
                continue
            if name and resource_group:
                if field.properties.get('name') == name and field.resource_group == resource_group:
                    yield field
            elif name and parent:
                if field.properties.get('name') == name and field.properties['parent'] == parent:
                    yield field
            elif resource_group:
                if field.resource_group == resource_group:
                    yield field
            elif parent:
                if field.properties['parent'] == parent:
                    yield field
            elif name:
                if field.properties.get('name') == name:
                    yield field
            else:
                yield field

    def _merge_properties(
            self,
            current_properties: 'MachineLearningWorkspaceResource',
            new_properties: 'MachineLearningWorkspaceResource',
            *,
            parameters: Dict[str, Parameter],
            symbol: ResourceSymbol,
            fields: FieldsType,
            resource_group: ResourceSymbol,
            **kwargs
        ) -> Dict[str, Any]:
        output_config = super()._merge_properties(
            current_properties,
            new_properties,
            symbol=symbol,
            fields=fields,
            resource_group=resource_group,
            parameters=parameters,
            **kwargs
        )
        if 'properties' in current_properties and current_properties['kind'] in ['Project', 'Hub']:
            # TODO: Fix this recursive call problem....
            # We only want to run this on the first call, not subsequent ones.
            if not current_properties['properties'].get('primaryUserAssignedIdentity'):
                current_properties['properties']['primaryUserAssignedIdentity'] = parameters['managedIdentityId']
            if not current_properties['properties'].get('workspaceHubConfig'):
                current_properties['properties']['workspaceHubConfig'] = {}
            if not current_properties['properties']['workspaceHubConfig'].get('defaultWorkspaceResourceGroup'):
                current_properties['properties']['workspaceHubConfig']['defaultWorkspaceResourceGroup'] = ResourceGroup().id

            for searchservices in self._find_all_resource_match(fields, resource="Microsoft.Search/searchServices"):
                search_connection = AIConnection(
                    {'parent': symbol},  # We have to do this to prevent infinit recursion on calling self.parent.__bicep__()
                    parent=self,
                    category='CognitiveSearch',
                    target=searchservices.outputs['endpoint'],
                    name=Guid(searchservices.properties.get('name', parameters['defaultName']), 'connection', self.properties['kind'], 'AISearch'),
                    metadata={
                        'ApiType': 'Azure',
                        'ResourceId': searchservices.symbol.id,
                        'location': self.properties.get('location', parameters['location'])
                    }
                )
                search_connection.__bicep__(fields, parameters=parameters)
            for aiservices in self._find_all_resource_match(fields, resource="Microsoft.CognitiveServices/accounts"):
                # TODO: This doesn't work if it's an existing resource reference
                # Add identifier to resource
                # Need to know the kind, because 
                # if aiservices.properties.get('kind') not in ['AIServices']:  # 'OpenAI'?
                #     continue
                # TODO: This will actually fail if there's more than one.... should more than one even be supported?
                ai_connection = AIConnection(
                    {'parent': symbol},
                    parent=self,
                    category='AIServices', # 'OpenAI
                    target=aiservices.outputs['endpoint'],
                    name=Guid(aiservices.properties.get('name', parameters['defaultName']), 'connection', self.properties['kind'], 'AIServices'),
                    metadata={
                        'ApiType': 'Azure',
                        'ResourceId': aiservices.symbol.id,
                        'location': self.properties.get('location', parameters['location'])
                    }
                )
                ai_connection.__bicep__(fields, parameters=parameters)
        return output_config



_DEFAULT_AI_HUB: 'MachineLearningWorkspaceResource' = {
    'kind': 'Hub',
    'name': GLOBAL_PARAMS['defaultName'].format("{}-hub"),
    'location': GLOBAL_PARAMS['location'],
    'tags': GLOBAL_PARAMS['azdTags'],
    'properties': {
        #'primaryUserAssignedIdentity': GLOBAL_PARAMS['managedIdentityId'],
        'publicNetworkAccess': 'Enabled',
        'enableDataIsolation': True,
        'v1LegacyMode': False,
        'hbiWorkspace': False,
        'managedNetwork': {
            'isolationMode': 'Disabled'
        }
    },
    'sku': {
        'name': 'Basic',
        'tier': 'Basic',
    },
    'identity': {
        'type': 'UserAssigned',
        'userAssignedIdentities': {GLOBAL_PARAMS['managedIdentityId'].format(): {}}
    }
}
_DEFAULT_AI_HUB_EXTENSIONS: ExtensionResources = {
    'managed_identity_roles': [],
    'user_roles': []
}

class AIHub(MLWorkspace[MachineLearningWorkspaceResourceType]):
    DEFAULTS: 'MachineLearningWorkspaceResource' = _DEFAULT_AI_HUB
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_HUB_EXTENSIONS
    resource: Literal["Microsoft.MachineLearningServices/workspaces"] = "Microsoft.MachineLearningServices/workspaces"
    properties: MachineLearningWorkspaceResourceType

    def __init__(
            self,
            properties: Optional['MachineLearningWorkspaceResource'] = None,
            /,
            name: Optional[str] = None,
            **kwargs: Unpack[MachineLearningWorkspaceKwargs]
    ) -> None:
        super().__init__(
            properties,
            name=name,
            kind="Hub",
            service_prefix=['aifoundry_hub'],
            identifier=ResourceIdentifiers.ai_hub,
            **kwargs
        )

    def _merge_properties(
            self,
            current_properties: 'MachineLearningWorkspaceResource',
            new_properties: 'MachineLearningWorkspaceResource',
            *,
            parameters: Dict[str, Parameter],
            symbol: ResourceSymbol,
            fields: FieldsType,
            resource_group: ResourceSymbol,
            **kwargs
        ) -> Dict[str, Any]:
        output_config = super()._merge_properties(
            current_properties,
            new_properties,
            symbol=symbol,
            fields=fields,
            resource_group=resource_group,
            parameters=parameters,
            **kwargs
        )
        if 'properties' in current_properties:
            # TODO: Fix this recursive call problem....
            # We only want to run this on the first call, not subsequent ones.
            if not current_properties['properties'].get('storageAccount'):
                storage = self._find_last_resource_match(fields, resource="Microsoft.Storage/storageAccounts")
                if not storage:
                    blob_storage = self._find_last_resource_match(fields, resource="Microsoft.Storage/storageAccounts/blobServices")
                    if not blob_storage:
                        raise ValueError("Cannot create AI Hub without associated Storage account.")
                    current_properties['properties']['storageAccount'] = blob_storage.properties['parent'].id
                else:
                    current_properties['properties']['storageAccount'] = storage.symbol.id
            if not current_properties['properties'].get('keyVault'):
                vault = self._find_last_resource_match(fields, resource="Microsoft.KeyVault/vaults")
                if not vault:
                    raise ValueError("Cannot create an AI Hub without associated KeyVault account.")
                current_properties['properties']['keyVault'] = vault.symbol.id
        return output_config


_DEFAULT_AI_PROJECT: 'MachineLearningWorkspaceResource' = {
    'kind': 'Project',
    'name': GLOBAL_PARAMS['defaultName'].format("{}-project"),
    'location': GLOBAL_PARAMS['location'],
    'tags': GLOBAL_PARAMS['azdTags'],
    'properties': {
        #'primaryUserAssignedIdentity': GLOBAL_PARAMS['managedIdentityId'],  # TODO direct global references are broken
        'publicNetworkAccess': 'Enabled',
        'enableDataIsolation': True,
        'v1LegacyMode': False,
        'hbiWorkspace': False,
    },
    'sku': {
        'name': 'Basic',
        'tier': 'Basic',
    },
    'identity': {
        'type': 'UserAssigned',
        'userAssignedIdentities': {GLOBAL_PARAMS['managedIdentityId'].format(): {}}
    }
}
_DEFAULT_AI_PROJECT_EXTENSIONS: ExtensionResources = {
    'managed_identity_roles': ['Contributor'],
    'user_roles': ['Contributor']
}

ClientType = TypeVar("ClientType", default='AIProjectClient')
class AIProject(MLWorkspace[MachineLearningWorkspaceResourceType]):
    DEFAULTS: 'MachineLearningWorkspaceResource' = _DEFAULT_AI_PROJECT
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_AI_PROJECT_EXTENSIONS
    resource: Literal["Microsoft.MachineLearningServices/workspaces"] = "Microsoft.MachineLearningServices/workspaces"
    properties: MachineLearningWorkspaceResourceType

    def __init__(
            self,
            properties: Optional['MachineLearningWorkspaceResource'] = None,
            /,
            name: Optional[str] = None,
            **kwargs: Unpack[MachineLearningWorkspaceKwargs]
    ) -> None:
        super().__init__(
            properties,
            name=name,
            kind="Project",
            service_prefix=['aifoundry_project'],
            identifier=ResourceIdentifiers.ai_project,
            **kwargs
        )
        self._settings['endpoint'] = StoredPrioritizedSetting(
            name='endpoint',
            env_vars=_build_envs(self._prefixes, ['ENDPOINT']),
            suffix=self._suffix
        )

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            resource_group: Union[str, ResourceSymbol],
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, resource_group=resource_group, **kwargs)
        outputs['endpoint'] = Output(
            f"AZURE_AIFOUNDRY_PROJECT_ENDPOINT{self._suffix}",
            "properties.discoveryUrl",
             symbol
        )
        return outputs

    def _merge_properties(
            self,
            current_properties: 'MachineLearningWorkspaceResource',
            new_properties: 'MachineLearningWorkspaceResource',
            *,
            parameters: Dict[str, Parameter],
            symbol: ResourceSymbol,
            fields: FieldsType,
            resource_group: ResourceSymbol,
            **kwargs
        ) -> Dict[str, Any]:
        output_config = super()._merge_properties(
            current_properties,
            new_properties,
            symbol=symbol,
            fields=fields,
            resource_group=resource_group,
            parameters=parameters,
            **kwargs
        )
        if 'properties' in current_properties:
            # TODO: Fix this recursive call problem....
            # We only want to run this on the first call, not subsequent ones.
            if not current_properties['properties'].get('hubResourceId'):
                hub: Optional[FieldType] = None
                for workspace in self._find_all_resource_match(fields, resource="Microsoft.MachineLearningServices/workspaces"):
                    if workspace.properties['kind'] == 'Hub':
                        hub = workspace
                        break
                if not hub:
                    raise ValueError("Cannot create AI Project without assiciated AI Hub.")
                current_properties['properties']['hubResourceId'] = hub.symbol.id
        return output_config

    def _build_credential(self, use_async: bool, *, config_store: Mapping[str, Any]) -> Union[SupportsTokenInfo, AsyncSupportsTokenInfo]:
        # TODO
        value = 'default' #self._settings['credential'](config_store=config_store)
        try:
            value = value.lower()
            if value == 'default':
                if use_async:
                    from azure.identity.aio import DefaultAzureCredential
                else:
                    from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential()
                # self._settings['credential'].set_value(credential)
                return credential
            if value == 'managedidentity':
                if use_async:
                    from azure.identity.aio import ManagedIdentityCredential
                else:
                    from azure.identity import ManagedIdentityCredential
                credential = ManagedIdentityCredential()
                # self._settings['credential'].set_value(credential)
                return credential
        except AttributeError:
            pass
        try:
            constructed_value = value()
            # self._settings['credential'].set_value(constructed_value)
            return constructed_value
        except TypeError:
            if isinstance(value, (SupportsTokenInfo, AsyncSupportsTokenInfo)):
                # self._settings['credential'].set_value(value)
                return value
        raise ValueError(f'Cannot convert {value} to credential type.')

    def get_client(
            self,
            cls: Optional[Callable[..., ClientType]] = None,
            *,
            transport: Any = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
            use_async: Optional[bool] = None,
            **client_options,
    ) -> ClientType:
        if env_name:
           if config_store:
               raise ValueError("Cannot specify both 'config_store' and 'env_name'.")
           config_store = _load_dev_environment(env_name)
        elif config_store is None:
            config_store = _load_dev_environment()

        if hasattr(cls, 'from_resource'):
            return cls.from_resource(self, config_store, transport=transport, **client_options)
        if hasattr(cls, '_from_resource'):
            return cls._from_resource(self, config_store, transport=transport, **client_options)

        if cls is None:
            if use_async:
                from azure.ai.projects.aio import AIProjectClient
                cls = AIProjectClient
            else:
                from azure.ai.projects import AIProjectClient
                cls = AIProjectClient
                use_async = False
        return cls(
            endpoint=self._settings['endpoint'](config_store=config_store).rstrip('/discovery/').lstrip('https://'),
            subscription_id=self._settings['subscription'](config_store=config_store),
            resource_group_name=self._settings['resource_group'](config_store=config_store),
            project_name=self._settings['name'](config_store=config_store),
            credential=self._build_credential(use_async, config_store=config_store)
        )