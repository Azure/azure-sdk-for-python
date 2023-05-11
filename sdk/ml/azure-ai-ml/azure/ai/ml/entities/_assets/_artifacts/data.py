# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
import re
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Type, Union

from azure.ai.ml._exception_helper import log_and_raise_error
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DataContainer,
    DataContainerProperties,
    DataType,
    DataVersionBase,
    DataVersionBaseProperties,
    MLTableData,
    UriFileDataVersion,
    UriFolderDataVersion,
)
from azure.ai.ml._schema import DataSchema
from azure.ai.ml._utils._arm_id_utils import get_arm_id_object_from_id
from azure.ai.ml._utils.utils import is_url
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, SHORT_URI_FORMAT, AssetTypes
from azure.ai.ml.entities._assets import Artifact
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .artifact import ArtifactStorageInfo

DataAssetTypeModelMap: Dict[str, Type[DataVersionBaseProperties]] = {
    AssetTypes.URI_FILE: UriFileDataVersion,
    AssetTypes.URI_FOLDER: UriFolderDataVersion,
    AssetTypes.MLTABLE: MLTableData,
}


def getModelForDataAssetType(data_asset_type: str) -> Type[DataVersionBaseProperties]:
    model = DataAssetTypeModelMap.get(data_asset_type)
    if model is None:
        msg = "Unknown DataType {}".format(data_asset_type)
        err = ValidationException(
            message=msg,
            no_personal_data_message=msg,
            error_type=ValidationErrorType.INVALID_VALUE,
            target=ErrorTarget.DATA,
            error_category=ErrorCategory.USER_ERROR,
        )
        log_and_raise_error(err)
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
    :param type: The type of the asset. Valid values are uri_file, uri_folder, mltable. Defaults to uri_folder.
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
        type: str = AssetTypes.URI_FOLDER,  # pylint: disable=redefined-builtin
        **kwargs,
    ):
        self._skip_validation = kwargs.pop("skip_validation", False)
        self._mltable_schema_url = kwargs.pop("mltable_schema_url", None)
        self._referenced_uris = kwargs.pop("referenced_uris", None)
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
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Data":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        data_asset = Data._load_from_dict(yaml_data=data, context=context, **kwargs)

        return data_asset

    @classmethod
    def _load_from_dict(cls, yaml_data: Dict, context: Dict, **kwargs) -> "Data":
        return Data(**load_from_dict(DataSchema, yaml_data, context, **kwargs))

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return DataSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_container_rest_object(self) -> DataContainer:
        VersionDetailsClass = getModelForDataAssetType(self.type)
        return DataContainer(
            properties=DataContainerProperties(
                properties=self.properties,
                tags=self.tags,
                is_archived=False,
                data_type=VersionDetailsClass.data_type,
            )
        )

    def _to_rest_object(self) -> DataVersionBase:
        VersionDetailsClass = getModelForDataAssetType(self.type)
        data_version_details = VersionDetailsClass(
            description=self.description,
            is_anonymous=self._is_anonymous,
            tags=self.tags,
            is_archived=False,
            properties=self.properties,
            data_uri=self.path,
            auto_delete_setting=self.auto_delete_setting,
        )
        if VersionDetailsClass._attribute_map.get("referenced_uris") is not None:
            data_version_details.referenced_uris = self._referenced_uris
        return DataVersionBase(properties=data_version_details)

    @classmethod
    def _from_container_rest_object(cls, data_container_rest_object: DataContainer) -> "Data":
        data_rest_object_details: DataContainerProperties = data_container_rest_object.properties
        data = Data(
            name=data_container_rest_object.name,
            creation_context=SystemData._from_rest_object(data_container_rest_object.system_data),
            tags=data_rest_object_details.tags,
            properties=data_rest_object_details.properties,
            type=getDataAssetType(data_rest_object_details.data_type),
        )
        data.latest_version = data_rest_object_details.latest_version
        return data

    @classmethod
    def _from_rest_object(cls, data_rest_object: DataVersionBase) -> "Data":
        data_rest_object_details: DataVersionBaseProperties = data_rest_object.properties
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
            creation_context=SystemData._from_rest_object(data_rest_object.system_data),
            is_anonymous=data_rest_object_details.is_anonymous,
            referenced_uris=getattr(data_rest_object_details, "referenced_uris", None),
            auto_delete_setting=getattr(data_rest_object_details, "auto_delete_setting", None),
        )
        return data

    @classmethod
    def _resolve_cls_and_type(cls, data, params_override):
        from azure.ai.ml.entities._data_import.data_import import DataImport

        if "source" in data:
            return DataImport, None

        return cls, None

    def _update_path(self, asset_artifact: ArtifactStorageInfo) -> None:
        regex = r"datastores\/(.+)"
        # datastore_arm_id is null for registry scenario, so capture the full_storage_path
        if not asset_artifact.datastore_arm_id and asset_artifact.full_storage_path:
            self.path = asset_artifact.full_storage_path
        else:
            groups = re.search(regex, asset_artifact.datastore_arm_id)
            if groups:
                datastore_name = groups.group(1)
                self.path = SHORT_URI_FORMAT.format(datastore_name, asset_artifact.relative_path)
