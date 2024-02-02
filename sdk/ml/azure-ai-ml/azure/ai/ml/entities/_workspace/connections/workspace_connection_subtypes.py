# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, List, Optional

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import (
    CONNECTION_API_VERSION_KEY,
    CONNECTION_API_TYPE_KEY,
    CONNECTION_KIND_KEY,
    CONNECTION_ACCOUNT_NAME_KEY,
    CONNECTION_CONTAINER_NAME_KEY,
)
from azure.ai.ml.entities._credentials import ApiKeyConfiguration
from .workspace_connection import WorkspaceConnection


# Dev notes: Any new classes require modifying the elif chains in the following functions in the
# WorkspaceConnection parent class: _from_rest_object, _get_entity_class_from_type, _get_schema_class_from_type
@experimental
class AzureOpenAIWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections
    to Azure Open AI.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param api_type: The api type that this connection was created for. Defaults to Azure.
    :type api_type: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        api_type: str = "Azure",
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="azure_open_ai", credentials=credentials, **kwargs)

        if self.tags is not None:
            self.tags[CONNECTION_API_VERSION_KEY] = api_version
            self.tags[CONNECTION_API_TYPE_KEY] = api_type

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY, CONNECTION_API_TYPE_KEY]

    @property
    def api_version(self) -> Optional[str]:
        """The API version of the workspace connection.

        :return: The API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_VERSION_KEY in self.tags:
            res: str = self.tags[CONNECTION_API_VERSION_KEY]
            return res
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the workspace connection.

        :param value: The new api version to set.
        :type value: str
        """
        if self.tags is not None:
            self.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def api_type(self) -> Optional[str]:
        """The API type of the workspace connection.

        :return: The API type of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_TYPE_KEY in self.tags:
            res: str = self.tags[CONNECTION_API_TYPE_KEY]
            return res
        return None

    @api_type.setter
    def api_type(self, value: str) -> None:
        """Set the API type of the workspace connection.

        :param value: The new api type to set.
        :type value: str
        """
        if self.tags is not None:
            self.tags[CONNECTION_API_TYPE_KEY] = value

@experimental
class AzureAISearchWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to
    Azure AI Search.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_search", credentials=credentials, **kwargs)

        if self.tags is not None:
            self.tags[CONNECTION_API_VERSION_KEY] = api_version

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY]

    @property
    def api_version(self) -> Optional[str]:
        """The API version of the workspace connection.

        :return: The API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_VERSION_KEY in self.tags:
            res: str = self.tags[CONNECTION_API_VERSION_KEY]
            return res
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the workspace connection.

        :param value: The new api version to set.
        :type value: str
        """
        if self.tags is not None:
            self.tags[CONNECTION_API_VERSION_KEY] = value


@experimental
class AzureAIServiceWorkspaceConnection(WorkspaceConnection):
    """A Workspace Connection that is specifically designed for handling connections to an Azure AI Service.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param api_version: The api version that this connection was created for.
    :type api_version: Optional[str]
    :param kind: The kind of ai service that this connection points to. Valid inputs include:
        "AzureOpenAI", "ContentSafety", and "Speech".
    :type kind: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration,
        api_version: Optional[str] = None,
        kind: Optional[str] = None,
        **kwargs: Any,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(target=target, type="cognitive_service", credentials=credentials, **kwargs)

        if self.tags is not None:
            self.tags[CONNECTION_API_VERSION_KEY] = api_version
            self.tags[CONNECTION_KIND_KEY] = kind

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_API_VERSION_KEY, CONNECTION_KIND_KEY]

    @property
    def api_version(self) -> Optional[str]:
        """The API version of the workspace connection.

        :return: The API version of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_API_VERSION_KEY in self.tags:
            res: str = self.tags[CONNECTION_API_VERSION_KEY]
            return res
        return None

    @api_version.setter
    def api_version(self, value: str) -> None:
        """Set the API version of the workspace connection.

        :param value: The new api version to set.
        :type value: str
        """
        if self.tags is not None:
            self.tags[CONNECTION_API_VERSION_KEY] = value

    @property
    def kind(self) -> Optional[str]:
        """The kind of the workspace connection.

        :return: The kind of the workspace connection.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_KIND_KEY in self.tags:
            res: str = self.tags[CONNECTION_KIND_KEY]
            return res
        return None

    @kind.setter
    def kind(self, value: str) -> None:
        """Set the kind of the workspace connection.

        :param value: The new kind to set.
        :type value: str
        """
        self.tags[CONNECTION_KIND_KEY] = value


@experimental
class AzureBlobStoreWorkspaceConnection(WorkspaceConnection):
    """A connection to an Azure Blob Store. Connections of this type are read-only,
    creation operations with them are not supported, and this class is only meant to be
    instantiated from GET and LIST workspace connection operations.

    :param name: Name of the workspace connection.
    :type name: str
    :param target: The URL or ARM resource ID of the external resource.
    :type target: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param credentials: The credentials for authenticating to the external resource.
    :type credentials: ~azure.ai.ml.entities.ApiKeyConfiguration
    :param container_name: The name of the container.
    :type container_name: str
    :param account_name: The name of the account.
    :type account_name: str
    """

    def __init__(
        self,
        *,
        target: str,
        credentials: ApiKeyConfiguration, # TODO: double check this
        container_name: str,
        account_name: str,
        **kwargs,
    ):
        kwargs.pop("type", None)  # make sure we never somehow use wrong type
        super().__init__(
            target=target,
            type="azure_blob",
            credentials=credentials,
            **kwargs
        )

        self.tags[CONNECTION_CONTAINER_NAME_KEY] = container_name
        self.tags[CONNECTION_ACCOUNT_NAME_KEY] = account_name

    @classmethod
    def _get_required_metadata_fields(cls) -> List[str]:
        return [CONNECTION_CONTAINER_NAME_KEY, CONNECTION_ACCOUNT_NAME_KEY]

    @property
    def container_name(self) -> str:
        """The name of the workspace connection's container.

        :return: The name of the container.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_CONTAINER_NAME_KEY in self.tags:
            return self.tags[CONNECTION_CONTAINER_NAME_KEY]
        return None
    
    @property
    def account_name(self) -> str:
        """The name of the workspace connection's account

        :return: The name of the account.
        :rtype: str
        """
        if self.tags is not None and CONNECTION_ACCOUNT_NAME_KEY in self.tags:
            return self.tags[CONNECTION_ACCOUNT_NAME_KEY]
        return None

# copilot shush AzureOneLake,  

       "PythonFeed",
        "ContainerRegistry",
        "Git",
        "S3",
        "Snowflake",
        "AzureSqlDb",
        "AzureSynapseAnalytics",
        "AzureMySqlDb",
        "AzurePostgresDb",
        "ADLSGen2",
        "Redis",
        "ApiKey",
        "AzureOpenAI",
        "CognitiveSearch",
        "CognitiveService",
        "CustomKeys",
        "AzureBlob",
        "AzureOneLake",
        "CosmosDb",
        "CosmosDbMongoDbApi",
        "AzureDataExplorer",
        "AzureMariaDb",
        "AzureDatabricksDeltaLake",
        "AzureSqlMi",
        "AzureTableStorage",
        "AmazonRdsForOracle",
        "AmazonRdsForSqlServer",
        "AmazonRedshift",
        "Db2",
        "Drill",
        "GoogleBigQuery",
        "Greenplum",
        "Hbase",
        "Hive",
        "Impala",
        "Informix",
        "MariaDb",
        "MicrosoftAccess",
        "MySql",
        "Netezza",
        "Oracle",
        "Phoenix",
        "PostgreSql",
        "Presto",
        "SapOpenHub",
        "SapBw",
        "SapHana",
        "SapTable",
        "Spark",
        "SqlServer",
        "Sybase",
        "Teradata",
        "Vertica",
        "Cassandra",
        "Couchbase",
        "MongoDbV2",
        "MongoDbAtlas",
        "AmazonS3Compatible",
        "FileServer",
        "FtpServer",
        "GoogleCloudStorage",
        "Hdfs",
        "OracleCloudStorage",
        "Sftp",
        "GenericHttp",
        "ODataRest",
        "Odbc",
        "GenericRest",
        "AmazonMws",
        "Concur",
        "Dynamics",
        "DynamicsAx",
        "DynamicsCrm",
        "GoogleAdWords",
        "Hubspot",
        "Jira",
        "Magento",
        "Marketo",
        "Office365",
        "Eloqua",
        "Responsys",
        "OracleServiceCloud",
        "PayPal",
        "QuickBooks",
        "Salesforce",
        "SalesforceServiceCloud",
        "SalesforceMarketingCloud",
        "SapCloudForCustomer",
        "SapEcc",
        "ServiceNow",
        "SharePointOnlineList",
        "Shopify",
        "Square",
        "WebTable",
        "Xero",
        "Zoho",
        "GenericContainerRegistry"