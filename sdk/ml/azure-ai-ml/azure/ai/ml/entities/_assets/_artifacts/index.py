# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union, cast

# cspell:disable-next-line
from azure.ai.ml._restclient.azure_ai_assets_v2024_04_01.azureaiassetsv20240401.models import Index as RestIndex
from azure.ai.ml._schema import IndexAssetSchema
from azure.ai.ml._utils._arm_id_utils import AMLAssetId, AMLNamedArmId
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, LONG_URI_FORMAT, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._assets._artifacts.artifact import ArtifactStorageInfo
from azure.ai.ml.entities._system_data import RestSystemData, SystemData
from azure.ai.ml.entities._util import load_from_dict


@experimental
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
    :vartype description: Optional[str]
    :ivar tags: Asset's tags.
    :vartype tags: Optional[dict[str, str]]
    :ivar properties: Asset's properties.
    :vartype properties: Optional[dict[str, str]]
    :ivar path: The local or remote path to the asset.
    :vartype path: Optional[Union[str, os.PathLike]]
    """

    def __init__(
        self,
        *,
        name: str,
        version: Optional[str] = None,
        stage: str = "Development",
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        properties: Optional[Dict[str, str]] = None,
        path: Optional[Union[str, PathLike]] = None,
        datastore: Optional[str] = None,
        **kwargs: Any,
    ):
        self.stage = stage
        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            path=path,
            datastore=datastore,
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, index_rest_object: RestIndex) -> "Index":
        """Convert the response from the Index API into a Index

        :param RestIndex index_rest_object:
        :return: An Index Asset
        :rtype: Index
        """
        asset_id = AMLAssetId(asset_id=index_rest_object.id)

        return Index(
            id=index_rest_object.id,
            name=asset_id.asset_name,
            version=asset_id.asset_version,
            description=index_rest_object.description,
            tags=index_rest_object.tags,
            properties=index_rest_object.properties,
            stage=index_rest_object.stage,
            path=index_rest_object.storage_uri,
            # pylint: disable-next=protected-access
            creation_context=SystemData._from_rest_object(
                RestSystemData.from_dict(index_rest_object.system_data.as_dict())
            ),
        )

    def _to_rest_object(self) -> RestIndex:
        # Note: Index.name and Index.version get dropped going to RestIndex, since both are encoded in the id
        #       (when present)
        return RestIndex(
            stage=self.stage,
            storage_uri=self.path,
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
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        return cast(Index, load_from_dict(IndexAssetSchema, data, context, **kwargs))

    def _to_dict(self) -> Dict:
        return cast(dict, IndexAssetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self))

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        """Updates an an artifact with the remote path of a local upload.

        :param ArtifactStorageInfo asset_artifact: The asset storage info of the artifact
        """
        aml_datastore_id = AMLNamedArmId(asset_artifact.datastore_arm_id)
        self.path = LONG_URI_FORMAT.format(
            aml_datastore_id.subscription_id,
            aml_datastore_id.resource_group_name,
            aml_datastore_id.workspace_name,
            aml_datastore_id.asset_name,
            asset_artifact.relative_path,
        )
