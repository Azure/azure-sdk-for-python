# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member

from abc import ABC
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import OneLakeDatastore as RestOneLakeDatastore, Datastore as DatastoreData, DatastoreType, OneLakeArtifact as RestOneLakeArtifact, LakeHouseArtifact as RestLakeHouseArtifact
from azure.ai.ml._schema._datastore.one_lake import OneLakeSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.entities._credentials import NoneCredentialConfiguration, ServicePrincipalConfiguration
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.entities._datastore.utils import from_rest_datastore_credentials
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.entities._util import load_from_dict


class OneLakeArtifact(RestTranslatableMixin, DictMixin, ABC):
    def __init__(
        self,
        artifact_name: str,
        artifact_type: Optional[str] = None
    ):
        super().__init__()
        self.artifact_name = artifact_name
        self.artifact_type = artifact_type


class LakeHouseArtifact(OneLakeArtifact):
    def __init__(
        self,
        artifact_name: str
    ):
        self.artifact_name = artifact_name
        self.artifact_type = "LakeHouse"

    def _to_datastore_rest_object(self) -> RestLakeHouseArtifact:
        return RestLakeHouseArtifact(artifact_name=self.artifact_name)


class OneLakeDatastore(Datastore):
    """OneLake datastore that is linked to an Azure ML workspace.

    :param name: Name of the datastore.
    :type name: str
    :param artifact: OneLake Artifact. Only LakeHouse artifacts are currently supported.
    :type artifact: ~azure.ai.ml.entities.OneLakeArtifact
    :param one_lake_workspace_name: OneLake workspace name/GUID. ex) 01234567-abcd-1234-5678-012345678901
    :type one_lake_workspace_name: str
    :param endpoint: OneLake endpoint to use for the datastore. ex) https://onelake.dfs.fabric.microsoft.com
    :type endpoint: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param credentials: Credentials to use to authenticate against OneLake.
    :type credentials: Union[
        ~azure.ai.ml.entities.ServicePrincipalConfiguration, ~azure.ai.ml.entities.NoneCredentialConfiguration]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str,
        artifact: OneLakeArtifact,
        one_lake_workspace_name: str,
        endpoint: Optional[str] = None, 
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        credentials: Optional[Union[NoneCredentialConfiguration, ServicePrincipalConfiguration]] = None,
        **kwargs
    ):
        kwargs[TYPE] = DatastoreType.ONE_LAKE
        super().__init__(
            name=name, description=description, tags=tags, properties=properties, credentials=credentials, **kwargs
        )
        self.artifact = artifact
        self.one_lake_workspace_name = one_lake_workspace_name
        self.endpoint = endpoint

    def _to_rest_object(self) -> DatastoreData:
        one_lake_ds = RestOneLakeDatastore(
            credentials=self.credentials._to_datastore_rest_object(),
            artifact=RestLakeHouseArtifact(artifact_name=self.artifact["artifact_name"]),
            one_lake_workspace_name=self.one_lake_workspace_name,
            endpoint=self.endpoint,
            description=self.description,
            tags=self.tags,
        )
        return DatastoreData(properties=one_lake_ds)

    @classmethod
    def _load_from_dict(
        cls, data: Dict, context: Dict, additional_message: str, **kwargs
    ) -> "OneLakeDatastore":
        return load_from_dict(OneLakeSchema, data, context, additional_message, **kwargs)

    @classmethod
    def _from_rest_object(cls, datastore_resource: DatastoreData):
        properties: RestOneLakeDatastore = datastore_resource.properties
        return OneLakeDatastore(
            name=datastore_resource.name,
            id=datastore_resource.id,
            artifact=properties.artifact,
            one_lake_workspace_name=properties.one_lake_workspace_name,
            endpoint=properties.endpoint,
            credentials=from_rest_datastore_credentials(properties.credentials),
            description=properties.description,
            tags=properties.tags,
        )

    def __eq__(self, other) -> bool:
        return (
            super().__eq__(other)
            and self.one_lake_workspace_name == other.one_lake_workspace_name
            and self.artifact == other.artifact
            and self.endpoint == other.endpoint
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def _to_dict(self) -> Dict:
        context = {BASE_PATH_CONTEXT_KEY: Path(".").parent}
        return OneLakeSchema(context=context).dump(self)
