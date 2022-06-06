# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import re
from typing import Dict, List, Optional, Tuple, Type, Union
from pathlib import Path
from os import PathLike

from azure.ai.ml.entities._assets import Artifact
from .artifact import ArtifactStorageInfo
from azure.ai.ml._utils.utils import is_url, load_yaml
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, SHORT_URI_FORMAT, AssetTypes
from azure.ai.ml._restclient.v2022_05_01.models import (
    DataContainerData,
    DataContainerDetails,
    DataType,
    DataVersionBaseData,
    DataVersionBaseDetails,
    UriFileDataVersion,
    UriFolderDataVersion,
    MLTableData,
)
from azure.ai.ml._utils._arm_id_utils import get_arm_id_object_from_id
from azure.ai.ml._schema import DataSchema
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget

DataAssetTypeModelMap: Dict[str, Tuple[Type[DataVersionBaseDetails], DataType]] = {
    AssetTypes.URI_FILE: (UriFileDataVersion, DataType.URI_FILE),
    AssetTypes.URI_FOLDER: (UriFolderDataVersion, DataType.URI_FOLDER),
    AssetTypes.MLTABLE: (MLTableData, DataType.MLTABLE),
}


def getModelForDataAssetType(data_asset_type: str) -> Tuple[Type[DataVersionBaseDetails], str]:
    model = DataAssetTypeModelMap.get(data_asset_type)
    if model is None:
        msg = "Unknown DataType {}".format(data_asset_type)
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.ARTIFACT,
            error_category=ErrorCategory.USER_ERROR,
        )
    return model


DataTypeMap: Dict[DataType, str] = {
    DataType.URI_FILE: AssetTypes.URI_FILE,
    DataType.URI_FOLDER: AssetTypes.URI_FOLDER,
    DataType.MLTABLE: AssetTypes.MLTABLE,
}


def getDataAssetType(data_type: DataType) -> str:
    return DataTypeMap.get(data_type, data_type)  # pass through value if no match found


class Data(Artifact):
    """Data for training and scoring.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param path: The path to the asset on the datastore. This can be local or remote
    :type path: str
    :param type: The type of the asset. Valid values are uri_file, uri_folder, mltable
    :type type: Literal[AssetTypes.URI_FILE, AssetTypes.URI_FOLDER, AssetTypes.MLTABLE]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        path: Optional[str] = None,  # if type is mltable, the path has to be a folder.
        type: str = AssetTypes.URI_FOLDER,  # type: ignore
        referenced_uris: Optional[List[str]] = None,
        **kwargs,
    ):
        self.type = type
        super().__init__(
            name=name,
            version=version,
            path=path,
            description=description,
            tags=tags,
            properties=properties,
            **kwargs,
        )
        self.referenced_uris = referenced_uris
        self.path = path

    @property
    def path(self) -> Optional[Union[str, PathLike]]:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        # Call the parent setter to resolve the path with base_path if it was a local path
        super(Data, type(self)).path.fset(self, value)
        if self.type == AssetTypes.URI_FOLDER and self._path is not None and not is_url(self._path):
            self._path = Path(os.path.join(self._path, ""))

    @classmethod
    def load(
        cls,
        path: Optional[Union[PathLike, str]],
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Data":
        """Construct a data object from yaml file.

        :param path: Path to a local file as the source.
        :type path: str
        :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
        :type params_override: list
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Constructed data object.
        :rtype: Data
        """
        yaml_dict = load_yaml(path)
        return cls._load(yaml_data=yaml_dict, yaml_path=path, params_override=params_override, **kwargs)

    @classmethod
    def _load(
        cls,
        yaml_data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Data":
        yaml_data = yaml_data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        data_asset = Data._load_from_dict(yaml_data=yaml_data, context=context, **kwargs)

        return data_asset

    @classmethod
    def _load_from_dict(cls, yaml_data: Dict, context: Dict, **kwargs) -> "Data":
        return Data(**load_from_dict(DataSchema, yaml_data, context, **kwargs))

    def _to_dict(self) -> Dict:
        return DataSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_container_rest_object(self) -> DataContainerData:
        _, data_type = getModelForDataAssetType(self.type)
        return DataContainerData(
            properties=DataContainerDetails(
                properties=self.properties, tags=self.tags, is_archived=False, data_type=data_type
            )
        )

    def _to_rest_object(self) -> DataVersionBaseData:
        VersionDetailsClass, _ = getModelForDataAssetType(self.type)
        data_version_details = VersionDetailsClass(
            description=self.description,
            is_anonymous=self._is_anonymous,
            tags=self.tags,
            is_archived=False,
            properties=self.properties,
            data_uri=self.path,
        )
        if VersionDetailsClass._attribute_map.get("referenced_uris") is not None:
            data_version_details.referenced_uris = self.referenced_uris
        return DataVersionBaseData(properties=data_version_details)

    @classmethod
    def _from_container_rest_object(cls, data_container_rest_object: DataContainerData) -> "Data":
        data_rest_object_details: DataContainerDetails = data_container_rest_object.properties
        data = Data(
            name=data_container_rest_object.name,
            creation_context=data_container_rest_object.system_data,
            tags=data_rest_object_details.tags,
            properties=data_rest_object_details.properties,
            type=getDataAssetType(data_rest_object_details.data_type),
        )
        data.latest_version = data_container_rest_object.properties.latest_version
        return data

    @classmethod
    def _from_rest_object(cls, data_rest_object: DataVersionBaseData) -> "Data":
        data_rest_object_details: DataVersionBaseDetails = data_rest_object.properties
        arm_id_object = get_arm_id_object_from_id(data_rest_object.id)
        path = data_rest_object_details.data_uri
        data = Data(
            id=data_rest_object.id,
            name=arm_id_object.asset_name,
            version=arm_id_object.asset_version,
            path=path,
            type=getDataAssetType(data_rest_object_details.data_type),
            description=data_rest_object_details.description,
            tags=data_rest_object_details.tags,
            properties=data_rest_object_details.properties,
            creation_context=data_rest_object.system_data,
            is_anonymous=data_rest_object_details.is_anonymous,
            referenced_uris=getattr(data_rest_object_details, "referenced_uris", None),
        )
        return data

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        regex = r"datastores\/(.+)"
        groups = re.search(regex, asset_artifact.datastore_arm_id)
        if groups:
            datastore_name = groups.group(1)
            self.path = SHORT_URI_FORMAT.format(datastore_name, asset_artifact.relative_path)
