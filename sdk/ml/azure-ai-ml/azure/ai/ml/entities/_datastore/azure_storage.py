# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from pathlib import Path
from typing import Dict, Union

from azure.ai.ml._azure_environments import _get_storage_endpoint_from_metadata
from azure.ai.ml._restclient.v2022_05_01.models import AzureBlobDatastore as RestAzureBlobDatastore
from azure.ai.ml._restclient.v2022_05_01.models import AzureDataLakeGen2Datastore as RestAzureDataLakeGen2Datastore
from azure.ai.ml._restclient.v2022_05_01.models import AzureFileDatastore as RestAzureFileDatastore
from azure.ai.ml._restclient.v2022_05_01.models import DatastoreData, DatastoreType
from azure.ai.ml._schema._datastore import AzureBlobSchema, AzureDataLakeGen2Schema, AzureFileSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._datastore.credentials import (
    AccountKeyCredentials,
    CertificateCredentials,
    SasTokenCredentials,
    ServicePrincipalCredentials,
)
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.entities._datastore.utils import from_rest_datastore_credentials
from azure.ai.ml.entities._util import load_from_dict

from ._constants import HTTPS


class AzureFileDatastore(Datastore):
    """Azure file share that is linked to an Azure ML workspace.

    :param name: Name of the datastore.
    :type name: str
    :param account_name: Name of the Azure storage account.
    :type account_name: str
    :param file_share_name: Name of the file share.
    :type file_share_name: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param endpoint: Endpoint to use to connect with the Azure storage account
    :type endpoint: str
    :param protocol: Protocol to use to connect with the Azure storage account
    :type protocol: str
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param credentials: Credentials to use for Azure ML workspace to connect to the storage.
    :type credentials: Union[AccountKeySection, SasSection]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        account_name: str,
        file_share_name: str,
        description: str = None,
        tags: Dict = None,
        endpoint: str = _get_storage_endpoint_from_metadata(),
        protocol: str = HTTPS,
        properties: Dict = None,
        credentials: Union[AccountKeyCredentials, SasTokenCredentials],
        **kwargs
    ):
        kwargs[TYPE] = DatastoreType.AZURE_FILE
        super().__init__(
            name=name, description=description, tags=tags, properties=properties, credentials=credentials, **kwargs
        )
        self.file_share_name = file_share_name
        self.account_name = account_name
        self.endpoint = endpoint
        self.protocol = protocol

    def _to_rest_object(self) -> DatastoreData:
        file_ds = RestAzureFileDatastore(
            account_name=self.account_name,
            file_share_name=self.file_share_name,
            credentials=self.credentials._to_rest_object(),
            endpoint=self.endpoint,
            protocol=self.protocol,
            description=self.description,
            tags=self.tags,
        )
        return DatastoreData(properties=file_ds)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "AzureFileDatastore":
        return load_from_dict(AzureFileSchema, data, context, additional_message)

    @classmethod
    def _from_rest_object(cls, datastore_resource: DatastoreData):
        properties: RestAzureFileDatastore = datastore_resource.properties
        return AzureFileDatastore(
            name=datastore_resource.name,
            id=datastore_resource.id,
            account_name=properties.account_name,
            credentials=from_rest_datastore_credentials(properties.credentials),
            endpoint=properties.endpoint,
            protocol=properties.protocol,
            file_share_name=properties.file_share_name,
            description=properties.description,
            tags=properties.tags,
        )

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.file_share_name == other.file_share_name
            and self.account_name == other.account_name
            and self.endpoint == other.endpoint
            and self.protocol == other.protocol
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def _to_dict(self) -> Dict:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return AzureFileSchema(context=context).dump(self)


class AzureBlobDatastore(Datastore):
    """Azure blob storage that is linked to an Azure ML workspace.

    :param name: Name of the datastore.
    :type name: str
    :param account_name: Name of the Azure storage account.
    :type account_name: str
    :param container_name: Name of the container.
    :type container_name: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param endpoint: Endpoint to use to connect with the Azure storage account.
    :type endpoint: str
    :param protocol: Protocol to use to connect with the Azure storage account.
    :type protocol: str
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param credentials: Credentials to use for Azure ML workspace to connect to the storage.
    :type credentials: Union[AccountKeySection, SasSection]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        account_name: str,
        container_name: str,
        description: str = None,
        tags: Dict = None,
        endpoint: str = _get_storage_endpoint_from_metadata(),
        protocol: str = HTTPS,
        properties: Dict = None,
        credentials: Union[AccountKeyCredentials, SasTokenCredentials] = None,
        **kwargs
    ):
        kwargs[TYPE] = DatastoreType.AZURE_BLOB
        super().__init__(
            name=name, description=description, tags=tags, properties=properties, credentials=credentials, **kwargs
        )

        self.container_name = container_name
        self.account_name = account_name
        self.endpoint = endpoint
        self.protocol = protocol

    def _to_rest_object(self) -> DatastoreData:
        blob_ds = RestAzureBlobDatastore(
            account_name=self.account_name,
            container_name=self.container_name,
            credentials=self.credentials._to_rest_object(),
            endpoint=self.endpoint,
            protocol=self.protocol,
            tags=self.tags,
            description=self.description,
        )
        return DatastoreData(properties=blob_ds)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "AzureBlobDatastore":
        return load_from_dict(AzureBlobSchema, data, context, additional_message)

    @classmethod
    def _from_rest_object(cls, datastore_resource: DatastoreData):
        properties: RestAzureBlobDatastore = datastore_resource.properties
        return AzureBlobDatastore(
            name=datastore_resource.name,
            id=datastore_resource.id,
            account_name=properties.account_name,
            credentials=from_rest_datastore_credentials(properties.credentials),
            endpoint=properties.endpoint,
            protocol=properties.protocol,
            container_name=properties.container_name,
            description=properties.description,
            tags=properties.tags,
        )

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.container_name == other.container_name
            and self.account_name == other.account_name
            and self.endpoint == other.endpoint
            and self.protocol == other.protocol
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def _to_dict(self) -> Dict:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return AzureBlobSchema(context=context).dump(self)


class AzureDataLakeGen2Datastore(Datastore):
    """Azure data lake gen 2 that is linked to an Azure ML workspace.

    :param name: Name of the datastore.
    :type name: str
    :param account_name: Name of the Azure storage account.
    :type account_name: str
    :param filesystem: The name of the Data Lake Gen2 filesystem.
    :type filesystem: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param endpoint: Endpoint to use to connect with the Azure storage account
    :type endpoint: str
    :param protocol: Protocol to use to connect with the Azure storage account
    :type protocol: str
    :param credentials: Credentials to use for Azure ML workspace to connect to the storage.
    :type credentials: Union[ServicePrincipalSection, CertificateSection]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        account_name: str,
        filesystem: str,
        description: str = None,
        tags: Dict = None,
        endpoint: str = _get_storage_endpoint_from_metadata(),
        protocol: str = HTTPS,
        properties: Dict = None,
        credentials: Union[ServicePrincipalCredentials, CertificateCredentials] = None,
        **kwargs
    ):
        kwargs[TYPE] = DatastoreType.AZURE_DATA_LAKE_GEN2
        super().__init__(
            name=name, description=description, tags=tags, properties=properties, credentials=credentials, **kwargs
        )

        self.account_name = account_name
        self.filesystem = filesystem
        self.endpoint = endpoint
        self.protocol = protocol

    def _to_rest_object(self) -> DatastoreData:
        gen2_ds = RestAzureDataLakeGen2Datastore(
            account_name=self.account_name,
            filesystem=self.filesystem,
            credentials=self.credentials._to_rest_object(),
            endpoint=self.endpoint,
            protocol=self.protocol,
            description=self.description,
            tags=self.tags,
        )
        return DatastoreData(properties=gen2_ds)

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, **kwargs
    ) -> "AzureDataLakeGen2Datastore":
        return load_from_dict(AzureDataLakeGen2Schema, data, context, additional_message)

    @classmethod
    def _from_rest_object(cls, datastore_resource: DatastoreData):
        properties: RestAzureDataLakeGen2Datastore = datastore_resource.properties
        return AzureDataLakeGen2Datastore(
            name=datastore_resource.name,
            id=datastore_resource.id,
            account_name=properties.account_name,
            credentials=from_rest_datastore_credentials(properties.credentials),
            endpoint=properties.endpoint,
            protocol=properties.protocol,
            filesystem=properties.filesystem,
            description=properties.description,
            tags=properties.tags,
        )

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.filesystem == other.filesystem
            and self.account_name == other.account_name
            and self.endpoint == other.endpoint
            and self.protocol == other.protocol
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def _to_dict(self) -> Dict:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return AzureDataLakeGen2Schema(context=context).dump(self)
