from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Self, Tuple, TypedDict, Union, Unpack, overload, Optional, Any, Type
from typing_extensions import TypeVar

from ..._identifiers import ResourceIdentifiers
from ...resourcegroup import ResourceGroup
from ...._parameters import GLOBAL_PARAMS
from ...._bicep.utils import generate_name
from ...._bicep.expressions import Expression, Output, Parameter, ResourceSymbol
from ...._setting import StoredPrioritizedSetting
from ...._resource import (
    ExtensionResources,
    ResourceReference,
    _ClientResource,
    _build_envs,
    FieldType,
    FieldsType
)

if TYPE_CHECKING:
    from .. import AIHub
    from ...._component import AzureInfrastructure
    from .types import ConnectionResource


class ConnectionKwargs(TypedDict, total=False):
    """"""
    category: Literal['ADLSGen2', 'AIServices', 'AmazonMws', 'AmazonRdsForOracle', 'AmazonRdsForSqlServer', 'AmazonRedshift', 'AmazonS3Compatible', 'ApiKey', 'AzureBlob', 'AzureDatabricksDeltaLake', 'AzureDataExplorer', 'AzureMariaDb', 'AzureMySqlDb', 'AzureOneLake', 'AzureOpenAI', 'AzurePostgresDb', 'AzureSqlDb', 'AzureSqlMi', 'AzureSynapseAnalytics', 'AzureTableStorage', 'BingLLMSearch', 'Cassandra', 'CognitiveSearch', 'CognitiveService', 'Concur', 'ContainerRegistry', 'CosmosDb', 'CosmosDbMongoDbApi', 'Couchbase', 'CustomKeys', 'Db2', 'Drill', 'Dynamics', 'DynamicsAx', 'DynamicsCrm', 'Eloqua', 'FileServer', 'FtpServer', 'GenericContainerRegistry', 'GenericHttp', 'GenericRest', 'Git', 'GoogleAdWords', 'GoogleBigQuery', 'GoogleCloudStorage', 'Greenplum', 'Hbase', 'Hdfs', 'Hive', 'Hubspot', 'Impala', 'Informix', 'Jira', 'Magento', 'MariaDb', 'Marketo', 'MicrosoftAccess', 'MongoDbAtlas', 'MongoDbV2', 'MySql', 'Netezza', 'ODataRest', 'Odbc', 'Office365', 'OpenAI', 'Oracle', 'OracleCloudStorage', 'OracleServiceCloud', 'PayPal', 'Phoenix', 'PostgreSql', 'Presto', 'PythonFeed', 'QuickBooks', 'Redis', 'Responsys', 'S3', 'Salesforce', 'SalesforceMarketingCloud', 'SalesforceServiceCloud', 'SapBw', 'SapCloudForCustomer', 'SapEcc', 'SapHana', 'SapOpenHub', 'SapTable', 'Serp', 'Serverless', 'ServiceNow', 'Sftp', 'SharePointOnlineList', 'Shopify', 'Snowflake', 'Spark', 'SqlServer', 'Square', 'Sybase', 'Teradata', 'Vertica', 'WebTable', 'Xero', 'Zoho']
    """Category of the connection."""
    connection_properties: Dict[str, object]
    """The properties of the connection, specific to the auth type."""
    target: str
    """The target of the connection."""
    expiry_time: str
    """The expiry time of the connection."""
    is_shared_to_all: bool
    """Indicates whether the connection is shared to all users in the workspace."""
    metadata: Dict[str, object]
    """User metadata for the connection."""
    shared_user_list: List[object]
    """The shared user list of the connection."""


_DEFAULT_CONNECTION: 'ConnectionResource' = {
    'properties': {
        'authType': 'AAD',
        'isSharedToAll': True,
        'sharedUserList': []
    }
}
ConnectionResourceType = TypeVar('ConnectionResourceType', default='ConnectionResource')


class AIConnection(_ClientResource[ConnectionResourceType]):
    DEFAULTS: 'ConnectionResource' = _DEFAULT_CONNECTION
    resource: Literal["Microsoft.MachineLearningServices/workspaces/connections"]
    properties: ConnectionResourceType
    parent: Union['AIHub', 'AIProject']

    def __init__(
            self,
            properties: Optional['ConnectionResource'] = None,
            /,
            name: Optional[str] = None,
            parent: Optional[Union[str, 'AIHub']] = None,
            **kwargs: Unpack[ConnectionKwargs]
    ) -> None:
        from .. import AIHub
        existing = kwargs.pop('existing', False)
        extensions: ExtensionResources = defaultdict(list)
        parent = parent if isinstance(parent, AIHub) else AIHub(name=parent)
        properties = properties or {}
        if 'properties' not in properties:
            properties['properties'] = {}
        if name:
            properties['name'] = name
        if 'category' in kwargs:
            properties['properties']['category'] = kwargs.pop('category')
        if 'target' in kwargs:
            properties['properties']['target'] = kwargs.pop('target')
        if 'metadata' in kwargs:
            properties['properties']['metadata'] = kwargs.pop('metadata')
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="connections",
            service_prefix=["ai_connection"],
            identifier=ResourceIdentifiers.ai_connection,
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

    def _build_suffix(self, name):
        return "_" + generate_name(name.value)

    def _outputs(self, **kwargs) -> Dict[str, Output]:
        return {}

    # def _merge_properties(
    #         self,
    #         current_properties: 'ConnectionResource',
    #         new_properties: 'ConnectionResource',
    #         *,
    #         parameters: Dict[str, Parameter],
    #         symbol: ResourceSymbol,
    #         fields: FieldsType,
    #         resource_group: ResourceSymbol,
    #         **kwargs
    #     ) -> Dict[str, Any]:
    #     output_config = super()._merge_properties(
    #         current_properties,
    #         new_properties,
    #         symbol=symbol,
    #         fields=fields,
    #         resource_group=resource_group,
    #         parameters=parameters,
    #         **kwargs
    #     )
    #     if 'properties' in current_properties:
    #         # TODO: Fix this recursive call problem....
    #         # We only want to run this on the first call, not subsequent ones.
    #         if not current_properties['properties'].get('authType') and not current_properties['properties'].get('credentials'):
    #             current_properties['properties']['credentials'] = {
    #                 'clientId': parameters['managedIdentityClientId'],
    #                 'resourceId': parameters['managedIdentityId']
    #             }
    #     return output_config