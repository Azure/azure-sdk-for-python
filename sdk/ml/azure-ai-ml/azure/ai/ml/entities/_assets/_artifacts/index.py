# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from typing import Any, Dict, Optional, Union

# cspell:disable-next-line
from azure.ai.ml._restclient.azure_ai_assets_v2024_04_01.azureaiassetsv20240401.models import Index as RestIndex
from azure.ai.ml._utils._arm_id_utils import AMLAssetId
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.entities._system_data import RestSystemData, SystemData


class Index(Artifact):
    """Index asset.

    :ivar name: Name of the resource.
    :vartype name: str
    :ivar version: Version of the resource.
    :vartype version: str
    :ivar id: Fully qualified resource Id:
     azureml://workspace/{workspaceName}/indexes/{name}/versions/{version} of the index. Required.
    :vartype id: str
    :ivar stage: Update stage to 'Archive' for soft delete. Default is Development, which means the
     asset is under development. Required.
    :vartype stage: str
    :ivar description: Description information of the asset.
    :vartype description: str
    :ivar tags: Asset's tags.
    :vartype tags: dict[str, str]
    :ivar properties: Asset's properties.
    :vartype properties: dict[str, str]
    :ivar str storage_uri: Default workspace blob storage Uri.
    :vartype storage_uri: str
    """

    def __init__(
        self,
        *,
        name: str,
        version: str,
        stage: str,
        storage_uri: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        properties: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ):
        self.stage = stage
        self.storage_uri = storage_uri
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, index_rest_object: RestIndex) -> "Index":
        """Convert the response from the Index API into a Index

        :param RestIndex index_rest_object:
        :return: An Index Asset
        :rtype: Index
        """
        asset_id = AMLAssetId(asset_id=index_rest_object.properties["id"])

        # FIXME: The typespec's definition of Index doesn't seem to match the actual response returned from the
        #        generic asset API (fields are nested into "properties" instead of top level).
        #        Manually handle this until the typespec is updated

        properties = index_rest_object["properties"]

        return Index(
            id=properties["id"],
            name=asset_id.asset_name,
            version=asset_id.asset_version,
            description=properties.get("description"),
            tags=properties.get("tags"),
            properties=properties,
            stage=properties.get("stage"),
            storage_uri=index_rest_object.storage_uri,
            # pylint: disable-next=protected-access
            creation_context=SystemData._from_rest_object(RestSystemData.from_dict(properties["systemData"])),
        )

    def _to_rest_object(self) -> RestIndex:
        return RestIndex(
            stage=self.stage,
            storage_uri=self.storage_uri,
            description=self.description,
            tags=self.tags,
            properties=self.properties,
            id=self.id,
        )

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Index":
        raise NotImplementedError()

    def _to_dict(self) -> Dict:
        raise NotImplementedError()

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        """Updates an an artifact with the remote path of a local upload.

        :param ArtifactStorageInfo asset_artifact: The asset storage info of the artifact
        :return: Nothing
        :rtype: None
        """
        raise NotImplementedError()
