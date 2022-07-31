# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
from os import PathLike

from azure.ai.ml.entities._assets.asset import Asset
from .artifact import ArtifactStorageInfo
from azure.ai.ml._utils.utils import load_yaml
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, SHORT_URI_FORMAT
from azure.ai.ml._restclient.v2021_10_01.models import (
    DatasetVersionDetails,
    DatasetVersionData,
    DatasetContainerData,
    UriReference,
)
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId, AMLNamedArmId
from azure.ai.ml._schema.assets.dataset import DatasetSchema
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


module_logger = logging.getLogger(__name__)


class Dataset(Asset):
    """Data for training and scoring.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param local_path: The local path to the asset.
    :type local_path: Union[str, os.PathLike]
    :param paths: The remote paths to the assets on the datastore.
    :type paths: List
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        description: str = None,
        tags: Dict = None,
        local_path: Optional[Union[str, PathLike]] = None,
        paths: List[UriReference] = None,
        properties: Dict = None,
        **kwargs,
    ):

        super().__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )

        self.paths = paths if paths is not None else []
        self.local_path = local_path

    @property
    def local_path(self) -> Optional[Union[str, PathLike]]:
        return self._local_path

    @local_path.setter
    def local_path(self, value) -> None:
        self._local_path = Path(self.base_path, value).resolve() if (value and self.base_path) else value

    def _validate(self) -> None:
        if (not self.local_path) and (not self.paths):
            msg = "Either paths or local_path need to be provided."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.DATASET,
            )

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str],
        params_override: list = None,
        **kwargs,
    ) -> "Dataset":
        """Construct a dataset object from yaml file.

        :param path: Path to a local file as the source.
        :type path: str
        :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
        :type params_override: List[Dict]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Constructed dataset object.
        :rtype: Dataset
        """
        yaml_dict = load_yaml(path)
        return cls._load(yaml_data=yaml_dict, yaml_path=path, params_override=params_override, **kwargs)

    @classmethod
    def _load(
        cls,
        yaml_data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Dataset":
        yaml_data = yaml_data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        return load_from_dict(DatasetSchema, yaml_data, context, **kwargs)

    def _to_dict(self) -> Dict:
        return DatasetSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _from_rest_object(cls, data_rest_object: DatasetVersionData) -> "Dataset":
        rest_data_version = data_rest_object.properties
        arm_id = AMLVersionedArmId(arm_id=data_rest_object.id)
        dataset = Dataset(
            id=data_rest_object.id,
            name=arm_id.asset_name,
            version=arm_id.asset_version,
            paths=rest_data_version.paths,
            description=rest_data_version.description,
            tags=rest_data_version.tags,
            properties=rest_data_version.properties,
            creation_context=data_rest_object.system_data,
            is_anonymous=data_rest_object.properties.is_anonymous,
        )
        return dataset

    def _to_rest_object(self) -> DatasetVersionData:
        data_version = DatasetVersionDetails(
            paths=self.paths,
            description=self.description,
            is_anonymous=self._is_anonymous,
            tags=self.tags,
            properties=self.properties,
        )
        dataset_version_resource = DatasetVersionData(properties=data_version)
        return dataset_version_resource

    @classmethod
    def _from_container_rest_object(cls, data_container_rest_object: DatasetContainerData) -> "Dataset":
        dataset = Dataset(
            name=data_container_rest_object.name,
            id=data_container_rest_object.id,
            version="1",
            creation_context=data_container_rest_object.system_data,
        )
        dataset.latest_version = data_container_rest_object.properties.latest_version

        # Setting version to None since if version is not provided it is defaulted to "1".
        # This should go away once container concept is finalized.
        dataset.version = None
        return dataset

    def _update_path(self, asset_artifact: ArtifactStorageInfo, **kwargs) -> None:
        """Updates an an artifact with the remote path of a local upload"""
        path = asset_artifact.relative_path
        datastore = AMLNamedArmId(asset_artifact.datastore_arm_id).asset_name
        uri = SHORT_URI_FORMAT.format(datastore, path)
        self.paths = []
        if asset_artifact.is_file:
            self.paths.append(UriReference(file=uri))
        else:
            # this is a temp solution as the backend logic need to support multiple path in future
            uri = SHORT_URI_FORMAT.format(datastore, path + "/")
            self.paths.append(UriReference(folder=uri))
