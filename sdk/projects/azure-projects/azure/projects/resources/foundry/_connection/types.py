# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

from ...._bicep.expressions import Parameter


RESOURCE = "Microsoft.MachineLearningServices/workspaces/connections"
VERSION = "2025-01-01-preview"


# TODO: This class is incomplete/incorrect
class ConnectionProperties(TypedDict, total=False):
    authType: Literal["AAD", "ManagedIdentity"]
    """"""
    credentials: Dict[str, str]
    """"""
    category: Required[
        Literal[
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
    ]
    """Category of the connection."""
    connectionProperties: Required[Dict[str, object]]
    """The properties of the connection, specific to the auth type."""
    target: Required[str]
    """The target of the connection."""
    expiryTime: str
    """The expiry time of the connection."""
    isSharedToAll: bool
    """Indicates whether the connection is shared to all users in the workspace."""
    metadata: Dict[str, str]
    """User metadata for the connection."""
    sharedUserList: List[object]
    """The shared user list of the connection."""
    useWorkspaceManagedIdentity: bool
    """"""


class ConnectionResource(TypedDict, total=False):
    name: Union[str, Parameter]
    """The resource name."""
    properties: "ConnectionProperties"
    """Properties of Connection."""
