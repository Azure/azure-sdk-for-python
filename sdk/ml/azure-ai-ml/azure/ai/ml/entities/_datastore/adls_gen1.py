# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    AzureDataLakeGen1Datastore as RestAzureDatalakeGen1Datastore,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import Datastore as DatastoreData
from azure.ai.ml._restclient.v2023_04_01_preview.models import DatastoreType
from azure.ai.ml._schema._datastore.adls_gen1 import AzureDataLakeGen1Schema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._credentials import CertificateConfiguration, ServicePrincipalConfiguration
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.entities._datastore.utils import from_rest_datastore_credentials
from azure.ai.ml.entities._util import load_from_dict


class AzureDataLakeGen1Datastore(Datastore):
    """Azure Data Lake aka Gen 1 datastore that is linked to an Azure ML workspace.

    :param name: Name of the datastore.
    :type name: str
    :param store_name: Name of the Azure storage resource.
    :type store_name: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param credentials: Credentials to use for Azure ML workspace to connect to the storage.
    :type credentials: Union[ServicePrincipalSection, CertificateSection]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        store_name: str,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        credentials: Optional[Union[CertificateConfiguration, ServicePrincipalConfiguration]] = None,
        **kwargs: Any
    ):
        kwargs[TYPE] = DatastoreType.AZURE_DATA_LAKE_GEN1
        super().__init__(
            name=name, description=description, tags=tags, properties=properties, credentials=credentials, **kwargs
        )

        self.store_name = store_name

    def _to_rest_object(self) -> DatastoreData:
        gen1_ds = RestAzureDatalakeGen1Datastore(
            credentials=self.credentials._to_datastore_rest_object(),
            store_name=self.store_name,
            description=self.description,
            tags=self.tags,
        )
        return DatastoreData(properties=gen1_ds)

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any
    ) -> "AzureDataLakeGen1Datastore":
        res: AzureDataLakeGen1Datastore = load_from_dict(
            AzureDataLakeGen1Schema, data, context, additional_message, **kwargs
        )
        return res

    @classmethod
    def _from_rest_object(cls, datastore_resource: DatastoreData) -> "AzureDataLakeGen1Datastore":
        properties: RestAzureDatalakeGen1Datastore = datastore_resource.properties
        return AzureDataLakeGen1Datastore(
            id=datastore_resource.id,
            name=datastore_resource.name,
            store_name=properties.store_name,
            credentials=from_rest_datastore_credentials(properties.credentials),  # type: ignore[arg-type]
            description=properties.description,
            tags=properties.tags,
        )

    def __eq__(self, other: Any) -> bool:
        res: bool = (
            super().__eq__(other)
            and self.name == other.name
            and self.type == other.type
            and self.store_name == other.store_name
            and self.credentials == other.credentials
        )
        return res

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def _to_dict(self) -> Dict:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        res: dict = AzureDataLakeGen1Schema(context=context).dump(self)
        return res
