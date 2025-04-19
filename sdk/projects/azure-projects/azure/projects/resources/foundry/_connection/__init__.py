# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    Union,
    Optional,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..._identifiers import ResourceIdentifiers
from ...._bicep.utils import generate_name
from ...._bicep.expressions import Output, Parameter, Expression, ResourceSymbol
from ...._resource import Resource

if TYPE_CHECKING:
    from .. import AIHub, AIProject
    from .types import ConnectionResource


class ConnectionKwargs(TypedDict, total=False):
    expiry_time: Union[str, Parameter]
    """The expiry time of the connection."""
    is_shared_to_all: Union[bool, Parameter]
    """Indicates whether the connection is shared to all users in the workspace."""
    metadata: Union[Dict[str, Union[str, Parameter]], Parameter]
    """User metadata for the connection."""
    shared_user_list: Union[List[Union[str, Parameter]], Parameter]
    """The shared user list of the connection."""


CategoryType = Literal[
    "ADLSGen2",
    "AIServices",
    "AmazonMws",
    "AmazonRdsForOracle",
    "AmazonRdsForSqlServer",
    "AmazonRedshift",
    "AmazonS3Compatible",
    "ApiKey",
    "AzureBlob",
    "AzureDatabricksDeltaLake",
    "AzureDataExplorer",
    "AzureMariaDb",
    "AzureMySqlDb",
    "AzureOneLake",
    "AzureOpenAI",
    "AzurePostgresDb",
    "AzureSqlDb",
    "AzureSqlMi",
    "AzureSynapseAnalytics",
    "AzureTableStorage",
    "BingLLMSearch",
    "Cassandra",
    "CognitiveSearch",
    "CognitiveService",
    "Concur",
    "ContainerRegistry",
    "CosmosDb",
    "CosmosDbMongoDbApi",
    "Couchbase",
    "CustomKeys",
    "Db2",
    "Drill",
    "Dynamics",
    "DynamicsAx",
    "DynamicsCrm",
    "Eloqua",
    "FileServer",
    "FtpServer",
    "GenericContainerRegistry",
    "GenericHttp",
    "GenericRest",
    "Git",
    "GoogleAdWords",
    "GoogleBigQuery",
    "GoogleCloudStorage",
    "Greenplum",
    "Hbase",
    "Hdfs",
    "Hive",
    "Hubspot",
    "Impala",
    "Informix",
    "Jira",
    "Magento",
    "MariaDb",
    "Marketo",
    "MicrosoftAccess",
    "MongoDbAtlas",
    "MongoDbV2",
    "MySql",
    "Netezza",
    "ODataRest",
    "Odbc",
    "Office365",
    "OpenAI",
    "Oracle",
    "OracleCloudStorage",
    "OracleServiceCloud",
    "PayPal",
    "Phoenix",
    "PostgreSql",
    "Presto",
    "PythonFeed",
    "QuickBooks",
    "Redis",
    "Responsys",
    "S3",
    "Salesforce",
    "SalesforceMarketingCloud",
    "SalesforceServiceCloud",
    "SapBw",
    "SapCloudForCustomer",
    "SapEcc",
    "SapHana",
    "SapOpenHub",
    "SapTable",
    "Serp",
    "Serverless",
    "ServiceNow",
    "Sftp",
    "SharePointOnlineList",
    "Shopify",
    "Snowflake",
    "Spark",
    "SqlServer",
    "Square",
    "Sybase",
    "Teradata",
    "Vertica",
    "WebTable",
    "Xero",
    "Zoho",
]
# TODO: Defaults will be missing required keys. Consider adding some kind of "Required" placeholder param.
_DEFAULT_CONNECTION: "ConnectionResource" = {
    "properties": {"authType": "AAD", "isSharedToAll": True, "sharedUserList": []}  # type: ignore[typeddict-item]
}
ConnectionResourceType = TypeVar("ConnectionResourceType", bound=Mapping[str, Any], default="ConnectionResource")


class AIConnection(Resource, Generic[ConnectionResourceType]):
    DEFAULTS: "ConnectionResource" = _DEFAULT_CONNECTION  # type: ignore[assignment]
    properties: ConnectionResourceType
    parent: Union["AIHub", "AIProject"]  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["ConnectionResource"] = None,
        /,
        name: Optional[Union[str, Expression]] = None,
        *,
        category: Union[CategoryType, Parameter],
        target: Union[str, Parameter],
        parent: Union["AIProject", "AIHub"],
        **kwargs: Unpack[ConnectionKwargs],
    ) -> None:
        properties = properties or {}
        if "properties" not in properties:
            properties["properties"] = {"category": category, "target": target}
        if category:
            properties["properties"]["category"] = category
        if target:
            properties["properties"]["target"] = target
        if name:
            properties["name"] = name
        # TODO: Rest of the kwargs support
        if "metadata" in kwargs:
            properties["properties"]["metadata"] = kwargs.pop("metadata")
        super().__init__(
            properties,
            parent=parent,
            subresource="connections",
            service_prefix=["ai_connection"],
            identifier=ResourceIdentifiers.ai_connection,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.MachineLearningServices/workspaces/connections"]:
        return "Microsoft.MachineLearningServices/workspaces/connections"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        if suffix:
            resource_ref = f"connection_{generate_name(suffix)}"
        else:
            resource_ref = "connection"
        return ResourceSymbol(resource_ref)

    def _outputs(self, **kwargs) -> Dict[str, List[Output]]:
        return {}
