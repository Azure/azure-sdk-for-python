# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from typing import Literal, List, Dict, Union
from typing_extensions import Required, TypedDict

from ...._bicep.expressions import Expression, ResourceSymbol, Parameter


VERSION = "2025-01-01-preview"


# TODO: This class is incomplete/incorrect
class ConnectionProperties(TypedDict, total=False):
    authType: Union[Literal["AAD", "ManagedIdentity"], Parameter]
    """"""
    credentials: Union[Dict[str, Union[str, Parameter]], Parameter]
    """"""
    category: Required[
        Union[
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
            ],
            Parameter,
        ]
    ]
    """Category of the connection."""
    target: Required[Union[str, Parameter]]
    """The target of the connection."""
    expiryTime: Union[str, Parameter]
    """The expiry time of the connection."""
    isSharedToAll: Union[bool, Parameter]
    """Indicates whether the connection is shared to all users in the workspace."""
    metadata: Union[Dict[str, Union[str, Parameter]], Parameter]
    """User metadata for the connection."""
    sharedUserList: Union[List[Union[str, Parameter]], Parameter]
    """The shared user list of the connection."""
    useWorkspaceManagedIdentity: Union[bool, Parameter]
    """"""


class ConnectionResource(TypedDict, total=False):
    name: Union[str, Expression]
    """The resource name."""
    properties: "ConnectionProperties"
    """Properties of Connection."""
    parent: ResourceSymbol
    """Parent of the Connection."""
